from typing import List

import ethereum
import pytest
from _pytest.monkeypatch import MonkeyPatch
from eth_utils import decode_hex
from web3 import Web3
from web3.contract import Contract

import microraiden.client.session
from ethevents.client.app import uCustomSession
from ethevents.test.config import WEI_ALLOWANCE, REI_ALLOWANCE
from microraiden import Session as uSession

from ethevents import App
from ethevents.test.utils import mock_prompt
from ethevents.types import Address, PrivateKeyHex
from microraiden.test.fixtures import fund_account


@pytest.fixture
def client_app(
        web3: Web3,
        channel_manager_address: Address,
        keystore_path: str,
        patched_contract
):
    app = App(
        web3=web3,
        channel_manager_address=channel_manager_address,
        keystore_path=keystore_path
    )

    return app


@pytest.fixture
def initialized_client_app(
        client_app: App,
        monkeypatch: MonkeyPatch,
        keyfiles: None,
        private_keys: List[PrivateKeyHex],
        addresses: List[Address],
        passwords: List[str],
        faucet_private_key: PrivateKeyHex,
        faucet_address: Address,
        web3: Web3,
        wait_for_transaction,
        token_contract: Contract,
        use_tester: bool
):
    i = 0

    fund_account(
        addresses[i],
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

    input_sequence = (value for value in [str(i), passwords[i]])
    mock_prompt(monkeypatch, input_sequence)
    client_app.start()

    assert client_app.account.unlocked
    assert client_app.session is not None

    request_original = uSession._request_resource

    def request_patched(self: uSession, method: str, url: str, **kwargs):
        if use_tester:
            self.client.context.web3.testing.mine(1)
        return request_original(self, method, url, **kwargs)
    monkeypatch.setattr(microraiden.client.session.Session, '_request_resource', request_patched)

    if use_tester:
        client_app.session.retry_interval = 0.1

    yield client_app

    client_app.drain(faucet_address, rdn_and_eth=True)


@pytest.fixture
def custom_session(
        monkeypatch: MonkeyPatch,
        web3: Web3,
        channel_manager_address: Address,
        sender_privkey: str,
        patched_contract,
        clean_channels,
        use_tester: bool
):
    session = uCustomSession(
        private_key=sender_privkey,
        web3=web3,
        channel_manager_address=channel_manager_address
    )

    request_original = uSession._request_resource

    def request_patched(self: uSession, method: str, url: str, **kwargs):
        if use_tester:
            self.client.context.web3.testing.mine(1)
        return request_original(self, method, url, **kwargs)
    monkeypatch.setattr(microraiden.client.session.Session, '_request_resource', request_patched)

    if use_tester:
        session.retry_interval = 0.1

    return session
