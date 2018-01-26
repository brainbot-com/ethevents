from typing import List

from _pytest.monkeypatch import MonkeyPatch
from eth_utils import is_address, encode_hex, to_checksum_address
from web3 import Web3
from web3.contract import Contract

from ethevents.client.app import App
from ethevents.test.utils import mock_prompt
from ethevents.types import Address
from ethevents.ui.account_ui import AccountUI
from microraiden.client import Channel
from microraiden.test.utils.client import close_channel_cooperatively
from microraiden.utils import keccak256


def test_account_ui(
        monkeypatch: MonkeyPatch,
        initialized_client_app: App,
        private_keys: List[str],
        addresses: List[str],
        web3: Web3,
        token_contract: Contract,
        faucet_address: Address,
        channel_manager_address: Address
):
    # Drain confirmation.
    input_sequence = (value for value in [True])
    mock_prompt(monkeypatch, input_sequence)

    app = initialized_client_app
    account_ui = AccountUI(app)

    assert account_ui.app is not None
    assert account_ui.ether_balance() > 0
    assert is_address(account_ui.address())
    assert account_ui.channel_balance() is None
    assert account_ui.channel_key() is None

    app.session.channel = app.session.client.open_channel(addresses[1], 10)
    app.session.channel.create_transfer(7)

    assert account_ui.channel_balance() == 7
    assert account_ui.channel_key() == encode_hex(keccak256(
        addresses[0],
        addresses[1],
        app.web3.eth.blockNumber
    ))

    account_ui.close_channel()
    assert app.session.channel.state == Channel.State.settling

    close_channel_cooperatively(app.session.channel, private_keys[1], channel_manager_address, 0)

    assert token_contract.call().balanceOf(addresses[0]) > 0
    account_ui.drain(to_checksum_address(faucet_address), rdn_and_eth=True)
    assert token_contract.call().balanceOf(addresses[0]) == 0
    assert web3.eth.getBalance(addresses[0]) == 0
