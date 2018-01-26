from typing import List
from unittest import mock

import ethereum
import pytest
import requests_mock
from _pytest.monkeypatch import MonkeyPatch
from eth_utils import decode_hex, to_normalized_address
from web3 import Web3
from web3.contract import Contract

from ethevents.client.app import App, uCustomSession
from ethevents.test.config import WEI_ALLOWANCE, REI_ALLOWANCE
from ethevents.test.utils import mock_prompt
from ethevents.types import Address, PrivateKeyHex
from microraiden import HTTPHeaders
from microraiden.test.fixtures import fund_account, sweep_account


def test_app_smoke(
        monkeypatch: MonkeyPatch,
        keyfiles: None,
        client_app: App,
        passwords: List[str]
):
    i = 0
    input_sequence = (value for value in [str(i), passwords[i]])
    mock_prompt(monkeypatch, input_sequence)

    client_app.start()


def test_app_insufficient_funds_abort(
        monkeypatch: MonkeyPatch,
        client_app: App,
        passwords: List[str]
):
    i = 2
    input_sequence = (value for value in [passwords[i], False])
    mock_prompt(monkeypatch, input_sequence)

    client_app.start()


def test_app_insufficient_funds_retry(
        monkeypatch: MonkeyPatch,
        keyfiles: None,
        client_app: App,
        passwords: List[str],
        private_keys: List[PrivateKeyHex],
        addresses: List[Address],
        token_contract: Contract,
        web3: Web3,
        wait_for_transaction,
        faucet_private_key: PrivateKeyHex,
        faucet_address: Address,
        use_tester: bool
):
    i = 3
    j = 4
    fund_account(
        addresses[j],
        WEI_ALLOWANCE,
        REI_ALLOWANCE,
        token_contract,
        web3,
        wait_for_transaction,
        faucet_private_key
    )
    if use_tester:
        ethereum.tester.accounts.append(decode_hex(addresses[j]))
        ethereum.tester.keys.append(decode_hex(private_keys[j]))
    input_sequence = (value for value in [i, True, j, passwords[j]])
    mock_prompt(monkeypatch, input_sequence)

    client_app.start()

    sweep_account(
        private_keys[j],
        faucet_address,
        token_contract,
        web3,
        wait_for_transaction
    )


def test_app_drain(
        monkeypatch: MonkeyPatch,
        keyfiles: None,
        client_app: App,
        passwords: List[str],
        private_keys: List[PrivateKeyHex],
        addresses: List[Address],
        web3: Web3,
        token_contract: Contract,
        faucet_address: Address,
        use_tester: bool,
        wait_for_transaction,
        faucet_private_key: PrivateKeyHex
):
    i = 6
    j = 3
    fund_account(
        addresses[i],
        WEI_ALLOWANCE,
        REI_ALLOWANCE,
        token_contract,
        web3,
        wait_for_transaction,
        faucet_private_key
    )
    fund_account(
        addresses[j],
        WEI_ALLOWANCE,
        REI_ALLOWANCE,
        token_contract,
        web3,
        wait_for_transaction,
        faucet_private_key
    )
    if use_tester:
        ethereum.tester.accounts.append(decode_hex(addresses[i]))
        ethereum.tester.keys.append(decode_hex(private_keys[i]))
        ethereum.tester.accounts.append(decode_hex(addresses[j]))
        ethereum.tester.keys.append(decode_hex(private_keys[j]))

    input_sequence = (value for value in [
        str(i),
        passwords[i],
        False,
        True,
        str(j),
        passwords[j],
        True
    ])
    mock_prompt(monkeypatch, input_sequence)

    client_app.start()

    account_rei = token_contract.call().balanceOf(addresses[i])
    account_wei = web3.eth.getBalance(addresses[i])
    faucet_rei = token_contract.call().balanceOf(faucet_address)
    faucet_wei = web3.eth.getBalance(faucet_address)
    assert account_rei > 0
    assert account_wei > 0

    # Should drain nothing.
    client_app.drain(faucet_address)
    assert token_contract.call().balanceOf(addresses[i]) == account_rei
    assert web3.eth.getBalance(addresses[i]) == account_wei

    with pytest.raises(AssertionError):
        # Address not checksummed.
        client_app.drain(to_normalized_address(faucet_address), rdn=True)

    # Not confirmed.
    client_app.drain(faucet_address, rdn=True)
    assert token_contract.call().balanceOf(addresses[i]) == account_rei
    assert web3.eth.getBalance(addresses[i]) == account_wei

    # Confirmed.
    client_app.drain(faucet_address, rdn=True)
    assert token_contract.call().balanceOf(addresses[i]) == 0
    assert 0 < web3.eth.getBalance(addresses[i]) < account_wei
    assert token_contract.call().balanceOf(faucet_address) == faucet_rei + account_rei
    assert web3.eth.getBalance(faucet_address) == faucet_wei

    # Second round, different account.
    client_app.start()

    account_rei = token_contract.call().balanceOf(addresses[j])
    account_wei = web3.eth.getBalance(addresses[j])
    faucet_rei = token_contract.call().balanceOf(faucet_address)
    faucet_wei = web3.eth.getBalance(faucet_address)
    assert account_rei > 0
    assert account_wei > 0

    # Drain both ETH and RDN.
    client_app.drain(faucet_address, rdn_and_eth=True)
    assert token_contract.call().balanceOf(addresses[j]) == 0
    assert web3.eth.getBalance(addresses[j]) == 0
    assert token_contract.call().balanceOf(faucet_address) == faucet_rei + account_rei
    assert web3.eth.getBalance(faucet_address) > faucet_wei


def test_custom_session_already_paid(
        custom_session: uCustomSession,
        token_address: str,
        channel_manager_address: str,
        receiver_address: str,
        api_endpoint_address: str
):
    custom_session.on_payment_requested = mock.Mock(wraps=custom_session.on_payment_requested)
    with requests_mock.mock() as server_mock:
        headers1 = {
            HTTPHeaders.TOKEN_ADDRESS: token_address,
            HTTPHeaders.CONTRACT_ADDRESS: channel_manager_address,
            HTTPHeaders.RECEIVER_ADDRESS: receiver_address,
            HTTPHeaders.PRICE: '3'
        }
        headers2 = headers1.copy()

        url = 'http://{}/something'.format(api_endpoint_address)
        server_mock.get(url, [
            {'status_code': 402, 'headers': headers1},
            {'status_code': 402, 'headers': headers2},
        ])
        response = custom_session.get(url)

    assert response.status_code == 402
    assert custom_session.channel.balance == 3
    assert custom_session.on_payment_requested.call_count == 2


def test_custom_session_price_cap(
        custom_session: uCustomSession,
        token_address: str,
        channel_manager_address: str,
        receiver_address: str,
        api_endpoint_address: str
):
    custom_session.on_payment_requested = mock.Mock(wraps=custom_session.on_payment_requested)
    with requests_mock.mock() as server_mock:
        headers = {
            HTTPHeaders.TOKEN_ADDRESS: token_address,
            HTTPHeaders.CONTRACT_ADDRESS: channel_manager_address,
            HTTPHeaders.RECEIVER_ADDRESS: receiver_address,
            HTTPHeaders.PRICE: '20001'
        }

        url = 'http://{}/something'.format(api_endpoint_address)
        server_mock.get(url, [
            {'status_code': 402, 'headers': headers},
        ])
        response = custom_session.get(url)

    assert response.status_code == 402
    assert custom_session.channel is None
    assert custom_session.on_payment_requested.call_count == 1
