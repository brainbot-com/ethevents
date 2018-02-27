from gevent import monkey       # see https://github.com/gevent/gevent/issues/941
monkey.patch_all(thread=False)  # monkey patch needs to happen before `import requests`
import logging

import click
from eth_utils import to_checksum_address, is_checksum_address, encode_hex
from requests import Response
from web3 import Web3, HTTPProvider

from ethevents.account_manager import AccountManagerCLI, Account  # flake8: noqa
from ethevents.config import (
    KEYSTORE_PATH,
    WEI_LIMIT,
    REI_LIMIT,
    TOKEN_SYMBOL,
    TOKEN_DECIMALS,
    WEI_THRESHOLD,
    REI_THRESHOLD
)
from ethevents.types import Address
from microraiden import Session as uSession, HTTPHeaders
from microraiden.constants import (
    CONTRACT_METADATA,
    TOKEN_ABI_NAME,
    CHANNEL_MANAGER_ABI_NAME,
    WEB3_PROVIDER_DEFAULT
)
from microraiden.config import NETWORK_CFG
from microraiden.utils import wait_for_transaction

log = logging.getLogger(__name__)


class uCustomSession(uSession):
    def __init__(self, max_rei_per_request: int = 50000, *args, **kwargs) -> None:
        uSession.__init__(self, *args, **kwargs)
        self.max_rei_per_request = max_rei_per_request

    def on_http_error(self, method: str, url: str, response: Response, **kwargs) -> bool:
        """Disable retry on error."""
        return False

    def on_payment_requested(self, method: str, url: str, response: Response, **kwargs) -> bool:
        price = int(response.headers[HTTPHeaders.PRICE])
        if price > self.max_rei_per_request:
            log.error(
                'Requested price exceeds configured maximum price per request ({} > {}). '
                'Aborting'.format(price, self.max_rei_per_request)
            )
            return False

        return uSession.on_payment_requested(self, method, url, response, **kwargs)


class App(object):
    def __init__(
            self,
            web3: Web3 = None,
            channel_manager_address: Address = NETWORK_CFG.CHANNEL_MANAGER_ADDRESS,
            keystore_path: str = KEYSTORE_PATH
    ):
        self.account = None  # type: Account
        self.web3 = web3
        if web3 is None:
            self.web3 = Web3(HTTPProvider(WEB3_PROVIDER_DEFAULT))

        self.session = None  # type: uSession

        self.channel_manager = self.web3.eth.contract(
            address=to_checksum_address(channel_manager_address),
            abi=CONTRACT_METADATA[CHANNEL_MANAGER_ABI_NAME]['abi']
        )

        token_address = self.channel_manager.call().token()
        self.token = self.web3.eth.contract(
            address=token_address,
            abi=CONTRACT_METADATA[TOKEN_ABI_NAME]['abi']
        )

        self.account_manager = AccountManagerCLI(
            keystore_path=keystore_path,
            web3=self.web3,
            token_address=self.token.address
        )

    def start(
            self,
            ignore_security_limits: bool = False,
            endpoint_url: str = None,
            max_rei_per_request: int = 50000
    ):
        self.account_manager.load_accounts()

        funds_ok = False
        while not funds_ok:
            self.account = self.account_manager.select_account()
            funds_ok = self.check_funds(ignore_security_limits)
            if not funds_ok:
                retry = click.confirm('Try again?')
                if not retry:
                    return
        self.account_manager.unlock_account(self.account)
        self.session = uCustomSession(
            private_key=self.account.private_key,
            web3=self.web3,
            channel_manager_address=self.channel_manager.address,
            endpoint_url=endpoint_url,
            max_rei_per_request=max_rei_per_request
        )

    def check_funds(self, ignore_security_limits) -> bool:
        self.account.sync_balances()
        assert self.account.wei_balance is not None
        assert self.account.rei_balance is not None

        limit_msg = 'The {symbol} balance of account {address} ({balance} {symbol}) exceeds the ' \
                    'security limit of {limit} {symbol}. ' \
                    'Please withdraw some of your {symbol} or select a different account.\n' \
                    'This account\'s private key can be found at {keyfile_path}\n' \
                    'You can use a wallet software of your choice to import this key.'

        threshold_msg = 'The {symbol} balance of account {address} ({balance} {symbol}) lies ' \
                        'below the required minimum of {threshold} {symbol}.\n' \
                        'Please deposit more {symbol} in your account, up to a maximum total of ' \
                        '{limit} {symbol}.'

        checksummed_address = to_checksum_address(self.account.address)
        if not ignore_security_limits and self.account.wei_balance > WEI_LIMIT:
            print(limit_msg.format(
                symbol='ETH',
                address=checksummed_address,
                balance=self.account.wei_balance / 10 ** 18,
                limit=WEI_LIMIT / 10 ** 18,
                keyfile_path=self.account.keyfile_path
            ))
            return False
        elif not ignore_security_limits and self.account.rei_balance > REI_LIMIT:
            print(limit_msg.format(
                symbol=TOKEN_SYMBOL,
                address=checksummed_address,
                balance=self.account.rei_balance / 10 ** TOKEN_DECIMALS,
                limit=REI_LIMIT / 10 ** TOKEN_DECIMALS,
                keyfile_path=self.account.keyfile_path
            ))
            return False
        elif self.account.wei_balance < WEI_THRESHOLD:
            print(threshold_msg.format(
                symbol='ETH',
                address=checksummed_address,
                balance=self.account.wei_balance / 10 ** 18,
                limit=WEI_LIMIT / 10 ** 18,
                threshold=WEI_THRESHOLD / 10 ** 18
            ))
            return False
        elif self.account.rei_balance < REI_THRESHOLD:
            print(threshold_msg.format(
                symbol=TOKEN_SYMBOL,
                address=checksummed_address,
                balance=self.account.rei_balance / 10 ** TOKEN_DECIMALS,
                limit=REI_LIMIT / 10 ** TOKEN_DECIMALS,
                threshold=REI_THRESHOLD / 10 ** TOKEN_DECIMALS
            ))
            return False

        return True

    def drain(self, to: Address, rdn: bool = False, rdn_and_eth: bool = False):
        if not rdn and not rdn_and_eth:
            print('Please specify either rdn=True or rdn_and_eth=True. No funds were moved.')
            return

        assert is_checksum_address(to), 'Sink address is not properly checksummed.'
        self.account.sync_balances()

        confirm = click.confirm(
            '{token_balance} {token_symbol} and {eth_balance} ETH (excluding transaction cost) '
            'will be moved to {to}.\n'
            'Are you sure you want to proceed?'.format(
                token_balance=self.account.rei_balance / 10 ** TOKEN_DECIMALS,
                token_symbol=TOKEN_SYMBOL,
                eth_balance=self.account.wei_balance / 10 ** 18,
                to=to
            )
        )

        if not confirm:
            return

        if self.account.rei_balance > 0 and (rdn or rdn_and_eth):
            tx_hash = self.account.drain_rdn(to)
            print('{} transfer sent. Transaction hash: {}'.format(
                TOKEN_SYMBOL,
                encode_hex(tx_hash)
            ))
            wait_for_transaction(self.web3, tx_hash)
        if self.account.wei_balance > NETWORK_CFG.GAS_PRICE * 21000 and rdn_and_eth:
            tx_hash = self.account.drain_eth(to)
            print('ETH transfer sent. Transaction hash: {}'.format(encode_hex(tx_hash)))
            wait_for_transaction(self.web3, tx_hash)
