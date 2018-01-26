import json
import re
from typing import List

import click
import os
import glob

import dateutil.parser
import pytz
from eth_utils import (
    keccak,
    to_checksum_address,
    encode_hex
)
from datetime import datetime
from eth_keyfile import create_keyfile_json, load_keyfile, decode_keyfile_json
from web3 import Web3

from ethevents.config import TOKEN_SYMBOL, KEYSTORE_PATH, TOKEN_DECIMALS, PASSWORD_ITERATIONS
from ethevents.types import KeyfileContent, Address, TXHashHex
from microraiden.config import NETWORK_CFG
from microraiden.constants import CONTRACT_METADATA, TOKEN_ABI_NAME
from microraiden.utils import create_signed_transaction, create_signed_contract_transaction


def keyfile_name(address: Address, time: datetime=None) -> str:
    if time is None:
        time = datetime.utcnow()
    return 'UTC--{y:04d}-{m:02d}-{d:02d}T{h:02d}-{min:02d}-{s:09.6f}Z--{address}'.format(
        y=time.year,
        m=time.month,
        d=time.day,
        h=time.hour,
        min=time.minute,
        s=time.second + time.microsecond / 1000000,
        address=(to_checksum_address(address))
    )


class Account(object):
    def __init__(
            self,
            keystore_path: str = None,
            keyfile_path: str = None,
            password: str = None,
            keyfile_content: KeyfileContent = None,
            web3: Web3 = None,
            token_address: Address = None
    ):
        assert keystore_path or keyfile_path, 'Either a keystore path or keyfile is required.'
        keyfile_exists = bool(keyfile_path) and os.path.exists(keyfile_path)
        assert keyfile_exists or keyfile_content or password, \
            'Password required for generating a new keyfile.'

        self.keyfile_path = keyfile_path
        self.keyfile_content = keyfile_content
        self.web3 = web3
        self.private_key = None
        self.created_at = None
        self.token = None
        self.wei_balance = None
        self.rei_balance = None

        if keyfile_exists:
            self.load_keyfile()
        elif not keyfile_content and password is not None:
            self.create_account(password)

        if self.locked and password is not None:
            self.unlock(password)

        assert self.keyfile_content, "Failed to load or generate a keyfile."
        self.address = to_checksum_address(self.keyfile_content['address'])

        if not keyfile_path:
            self.keyfile_path = os.path.join(keystore_path, keyfile_name(self.address))

        if not keyfile_exists:
            self.save_keyfile()

        if token_address is not None and self.web3 is not None:
            self.token = self.web3.eth.contract(
                address=token_address,
                abi=CONTRACT_METADATA[TOKEN_ABI_NAME]['abi']
            )

        self.get_creation_date()
        self.sync_balances()

    def load_keyfile(self):
        self.keyfile_content = load_keyfile(self.keyfile_path)
        assert self.keyfile_content['version'] == 3, 'Older keyfile versions not supported.'

    def create_account(self, password: str):
        self.private_key = keccak(os.urandom(4096))
        self.keyfile_content = create_keyfile_json(
            self.private_key,
            password.encode(),
            iterations=PASSWORD_ITERATIONS
        )
        self.private_key = encode_hex(self.private_key)

    def save_keyfile(self):
        with open(self.keyfile_path, 'w') as keyfile:
            json.dump(self.keyfile_content, keyfile)

    def get_creation_date(self):
        timestamp = self.keyfile_content.get('timestamp')
        if timestamp is not None and timestamp > 1000000000:
            self.created_at = datetime.utcfromtimestamp(timestamp)
        else:
            iso_regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}\.[0-9]{6}Z'
            keyfile_name = os.path.basename(self.keyfile_path)
            match = re.findall(iso_regex, keyfile_name)
            if match:
                date_string = match[0][:13] + ':' + match[0][14:16] + ':' + match[0][17:]
                self.created_at = dateutil.parser.parse(date_string)
            else:
                self.created_at = datetime.utcfromtimestamp(os.path.getmtime(self.keyfile_path))
        self.created_at = self.created_at.replace(tzinfo=pytz.UTC)

    @property
    def locked(self):
        return self.private_key is None

    @property
    def unlocked(self):
        return not self.locked

    def unlock(self, password: str):
        if self.unlocked:
            return
        self.private_key = encode_hex(decode_keyfile_json(self.keyfile_content, password.encode()))
        if self.token is not None:
            self.token.privkey = self.private_key

    def lock(self):
        self.private_key = None
        if self.token is not None:
            self.token.privkey = None

    def sync_balances(self):
        if not self.web3:
            print("Warning: No Web3 context available. Cannot get account ETH balance.")
        else:
            self.wei_balance = self.web3.eth.getBalance(self.address)

        if not self.token:
            print('Warning: No token contract available. Cannot get account {} balance.'.format(
                TOKEN_SYMBOL
            ))
        else:
            self.rei_balance = self.token.call().balanceOf(self.address)

    def drain_eth(self, to: Address) -> TXHashHex:
        assert self.web3
        assert self.unlocked, 'Account is locked.'
        wei = self.web3.eth.getBalance(self.address)

        tx = create_signed_transaction(
            self.private_key,
            self.web3,
            to=to,
            value=wei - 21000 * NETWORK_CFG.GAS_PRICE,
            gas_limit=21000
        )
        return self.web3.eth.sendRawTransaction(tx)

    def drain_rdn(self, to: Address) -> TXHashHex:
        assert self.web3
        assert self.token
        assert self.unlocked, 'Account is locked.'

        rei = self.token.call().balanceOf(self.address)
        tx = create_signed_contract_transaction(
            self.private_key,
            self.token,
            'transfer',
            [
                to,
                rei
            ]
        )
        return self.web3.eth.sendRawTransaction(tx)


class AccountManager(object):
    def __init__(
            self,
            keystore_path: str = KEYSTORE_PATH,
            web3: Web3 = None,
            token_address: Address = None
    ):
        self.web3 = web3
        self.token_address = token_address
        os.makedirs(keystore_path, exist_ok=True)
        self.keystore_path = keystore_path
        self.accounts = {}
        self.load_accounts()

    def load_accounts(self, keystore_path: str = None):
        if not keystore_path:
            keystore_path = self.keystore_path

        keyfile_paths = glob.glob(os.path.join(keystore_path, '*'))
        for keyfile_path in keyfile_paths:
            account = Account(
                keyfile_path=keyfile_path,
                web3=self.web3,
                token_address=self.token_address
            )
            self.accounts[account.address] = account


class AccountManagerCLI(AccountManager):
    def select_account(self):
        if not self.accounts:
            account = self.create_account()
        else:
            account = self.prompt_account_selection()
        return account

    def create_account(self) -> Account:
        password = click.prompt('Please enter a password for your new account', hide_input=True)
        account = Account(
            keystore_path=self.keystore_path,
            password=password,
            web3=self.web3,
            token_address=self.token_address
        )
        self.accounts[account.address] = account
        return account

    def prompt_account_selection(self) -> Account:
        accounts_sorted = sorted(self.accounts.values(), key=lambda account: account.created_at)

        if len(accounts_sorted) == 1:
            i = 0
        else:
            self.print_accounts(accounts_sorted)

            i = int(click.prompt('Please select an account to unlock', type=int))
            assert 0 <= i < len(self.accounts)

        account = accounts_sorted[i]

        return account

    def unlock_account(self, account: Account):
        for i in range(3):
            password = click.prompt('Please enter the password for account {}'.format(
                account.address
            ), hide_input=True)
            try:
                account.unlock(password)
                break
            except ValueError:
                print('Incorrect password ({}/3).'.format(i + 1, 3))

        if not account.unlocked:
            raise ValueError('Account {} could not be unlocked.'.format(account.address))

    @staticmethod
    def print_accounts(accounts_sorted: List[Account]):
        for i, account in enumerate(accounts_sorted):
            print('\t[{}] {}{}{}'.format(
                i,
                to_checksum_address(account.address),
                ' {:12.6f} ETH'.format(account.wei_balance / 10**18)
                if account.wei_balance is not None else '',
                ' {:12.6f} {}'.format(account.rei_balance / 10 ** TOKEN_DECIMALS, TOKEN_SYMBOL)
                if account.rei_balance is not None else ''
            ))
