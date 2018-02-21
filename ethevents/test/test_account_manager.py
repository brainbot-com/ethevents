import glob
import re
from pathlib import Path
from typing import List

import os

import ethereum
import pytest
import time
from datetime import datetime

import pytz
from _pytest.monkeypatch import MonkeyPatch
from eth_utils import is_same_address, is_checksum_address, decode_hex
from web3 import Web3
from web3.contract import Contract

from ethevents.account_manager import Account, AccountManager, AccountManagerCLI
from ethevents.test.config import WEI_ALLOWANCE
from ethevents.test.utils import mock_prompt
from ethevents.types import KeyfileContent, Address, PrivateKeyHex
from microraiden.config import NETWORK_CFG
from microraiden.test.fixtures import fund_account


def test_account_load_file(
        private_keys: List[PrivateKeyHex],
        keyfile_contents: List[KeyfileContent],
        keyfiles: None,
        keyfile_paths: List[str],
        passwords: List[str],
        addresses: List[Address]
):
    i = 0
    account = Account(keyfile_path=keyfile_paths[i])
    assert account.locked
    assert account.keyfile_content == keyfile_contents[i]
    assert account.keyfile_path == keyfile_paths[i]
    assert is_same_address(account.address, addresses[i])
    assert is_checksum_address(account.address)
    assert account.wei_balance is None
    assert account.rei_balance is None

    i = 1
    account = Account(keyfile_path=keyfile_paths[i], password=passwords[i])
    assert account.unlocked
    assert account.keyfile_content == keyfile_contents[i]
    assert account.keyfile_path == keyfile_paths[i]
    assert account.address == addresses[i]
    assert account.private_key == private_keys[i]


def test_account_load_file_funded(
        keyfiles: None,
        keyfile_paths: List[str],
        addresses: List[Address],
        passwords: List[str],
        web3: Web3,
        token_address: Address,
        token_contract: Contract,
        wait_for_transaction,
        faucet_private_key: PrivateKeyHex
):
    i = 3
    fund_account(
        addresses[i],
        5,
        3,
        token_contract,
        web3,
        wait_for_transaction,
        faucet_private_key
    )
    account = Account(
        keyfile_path=keyfile_paths[i],
        password=passwords[i],
        web3=web3,
        token_address=token_address
    )

    assert account.wei_balance == 5
    assert account.rei_balance == 3


def test_account_load_dict(
        private_keys: List[PrivateKeyHex],
        keyfile_contents: List[KeyfileContent],
        keystore_path: str,
        keyfile_paths: List[str],
        passwords: List[str],
        addresses: List[Address]
):
    i = 0
    assert not os.path.exists(keyfile_paths[i])

    with pytest.raises(AssertionError):
        # No keyfile or keystore specified.
        Account(keyfile_content=keyfile_contents[i])

    account = Account(keyfile_path=keyfile_paths[i], keyfile_content=keyfile_contents[i])
    assert account.locked
    assert account.keyfile_content == keyfile_contents[i]
    assert account.keyfile_path == keyfile_paths[i]
    assert account.address == addresses[i]
    assert os.path.exists(keyfile_paths[i])

    i = 1
    assert not os.path.exists(keyfile_paths[i])
    account = Account(
        keyfile_path=keyfile_paths[i],
        password=passwords[i],
        keyfile_content=keyfile_contents[i]
    )
    assert account.unlocked
    assert account.keyfile_content == keyfile_contents[i]
    assert account.keyfile_path == keyfile_paths[i]
    assert account.address == addresses[i]
    assert account.private_key == private_keys[i]
    assert os.path.exists(keyfile_paths[i])

    i = 2
    assert not os.path.exists(keyfile_paths[i])
    account = Account(
        keystore_path=keystore_path,
        password=passwords[i],
        keyfile_content=keyfile_contents[i]
    )
    assert account.unlocked
    assert account.keyfile_content == keyfile_contents[i]
    assert account.address == addresses[i]
    assert account.private_key == private_keys[i]
    assert os.path.exists(account.keyfile_path)
    assert len(glob.glob(keystore_path)) == 1


def test_account_generate(
        passwords: List[str],
        keystore_path: str,
        keyfile_paths: List[str]
):
    start_time = datetime.utcnow().replace(tzinfo=pytz.UTC)

    i = 0
    with pytest.raises(AssertionError):
        # No password specified.
        Account(keyfile_path=keyfile_paths[i])
    with pytest.raises(AssertionError):
        # No password specified.
        Account(keystore_path=keystore_path)

    i = 1
    keyfile_path = os.path.join(keystore_path, 'testkey')
    assert not os.path.exists(keyfile_paths[i])
    account = Account(keyfile_path=keyfile_path, password=passwords[i])
    assert account.unlocked
    assert account.private_key
    assert account.address
    created_at = account.created_at
    assert created_at > start_time
    assert os.path.exists(keyfile_path)

    address = account.address
    account = Account(keyfile_path=keyfile_path)
    assert account.locked
    assert account.address == address
    assert created_at == account.created_at

    i = 2
    assert not os.path.exists(keyfile_paths[i])
    account = Account(keyfile_path=keyfile_paths[i], password=passwords[i])
    assert account.unlocked
    assert account.private_key
    assert account.address
    assert account.created_at < start_time
    assert len(glob.glob(os.path.join(keystore_path, '*'))) == 2


def test_account_generate_in_keystore(
        passwords: List[str],
        keystore_path: str,
        keyfile_paths: List[str]
):
    i = 3
    assert not os.path.exists(keyfile_paths[i])
    account = Account(keystore_path=keystore_path, password=passwords[i])
    assert account.unlocked
    assert account.private_key
    assert account.address
    file_regex = 'UTC--[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}\.[0-9]{6}Z--'
    file_regex += account.address
    assert os.path.dirname(account.keyfile_path) == keystore_path
    assert re.match(file_regex, os.path.basename(account.keyfile_path))
    assert os.path.exists(account.keyfile_path)

    # Make sure the timestamp from the file name is used, not from mtime.
    time.sleep(0.1)
    Path(account.keyfile_path).touch(exist_ok=True)
    mtime = datetime.utcfromtimestamp(os.path.getmtime(account.keyfile_path))
    mtime = mtime.replace(tzinfo=pytz.UTC)
    assert account.created_at < mtime


def test_account_manager_load_keystore(
        num_accounts: int,
        keyfiles: None,
        keystore_path: str,
        addresses: List[Address]
):
    manager = AccountManager(keystore_path)
    assert len(manager.accounts) == num_accounts
    assert manager.accounts[addresses[0]].address == addresses[0]
    assert all(account.locked for account in manager.accounts.values())


def test_account_manager_cli_generate(
        monkeypatch: MonkeyPatch,
        keystore_path: str,
        passwords: List[str]
):
    i = 0
    input_sequence = (value for value in [passwords[i]])
    mock_prompt(monkeypatch, input_sequence)

    manager = AccountManagerCLI(keystore_path)
    account = manager.select_account()
    assert account.locked
    assert len(manager.accounts) == 1
    assert len(glob.glob(os.path.join(keystore_path, '*'))) == 1

    with pytest.raises(ValueError):
        # Wrong password.
        account.unlock(passwords[1])
    account.unlock(passwords[i])

    # Wrong password but ignored.
    try:
        account.unlock(passwords[1])
    except ValueError:
        assert False, "Already unlocked account is supposed to ignore wrong password."


def test_account_manager_cli_select(
        addresses: List[Address],
        monkeypatch: MonkeyPatch,
        keystore_path: str,
        keyfiles: None,
        passwords: List[str],
        web3: Web3,
        token_address: Address
):
    i = 2
    input_sequence = (value for value in ['2', passwords[i]])
    mock_prompt(monkeypatch, input_sequence)

    manager = AccountManagerCLI(keystore_path, web3=web3, token_address=token_address)
    account = manager.select_account()
    assert account.locked
    assert account.address == addresses[i]

    manager.unlock_account(account)
    assert account.unlocked

    account.lock()
    with pytest.raises(ValueError):
        # Wrong password.
        account.unlock(passwords[1])
    account.unlock(passwords[i])


def test_account_manager_cli_autoselect(
        monkeypatch: MonkeyPatch,
        keystore_path: str,
        passwords: List[str]
):
    i = 2
    input_sequence = (value for value in [passwords[i]])
    mock_prompt(monkeypatch, input_sequence)

    Account(keystore_path=keystore_path, password=passwords[i])
    manager = AccountManagerCLI(keystore_path)
    account = manager.select_account()
    assert account.locked

    manager.unlock_account(account)
    assert account.unlocked

    account.lock()
    with pytest.raises(ValueError):
        # Wrong password.
        account.unlock(passwords[1])
    account.unlock(passwords[i])


def test_account_manager_cli_select_wrong_password(
        monkeypatch: MonkeyPatch,
        keystore_path: str,
        keyfiles: None,
        passwords: List[str]
):
    input_sequence = (value for value in ['2', passwords[3], passwords[4], passwords[5]])
    mock_prompt(monkeypatch, input_sequence)

    manager = AccountManagerCLI(keystore_path)
    account = manager.select_account()
    with pytest.raises(ValueError):
        manager.unlock_account(account)


def test_account_drain(
        keyfile_paths: List[str],
        private_keys: List[PrivateKeyHex],
        passwords: List[str],
        web3: Web3,
        token_address: Address,
        wait_for_transaction,
        token_contract: Contract,
        keyfiles: None,
        addresses: List[Address],
        faucet_address: Address,
        faucet_private_key: PrivateKeyHex,
        use_tester: bool
):
    i = 1
    fund_account(
        addresses[i],
        WEI_ALLOWANCE,
        7,
        token_contract,
        web3,
        wait_for_transaction,
        faucet_private_key
    )

    if use_tester:
        ethereum.tester.accounts.append(decode_hex(addresses[i]))
        ethereum.tester.keys.append(decode_hex(private_keys[i]))

    account = Account(
        keyfile_path=keyfile_paths[i],
        password=passwords[i],
        web3=web3,
        token_address=token_address
    )
    assert account.unlocked
    assert account.wei_balance > 0
    assert account.rei_balance == 7

    account_rei = token_contract.call().balanceOf(account.address)
    faucet_rei = token_contract.call().balanceOf(faucet_address)

    tx_hash = account.drain_rdn(faucet_address)
    wait_for_transaction(tx_hash)

    account.sync_balances()
    assert account.rei_balance == 0
    assert account.wei_balance > 0
    assert token_contract.call().balanceOf(faucet_address) == faucet_rei + account_rei

    account_wei = web3.eth.getBalance(account.address)
    faucet_wei = web3.eth.getBalance(faucet_address)

    tx_hash = account.drain_eth(faucet_address)
    wait_for_transaction(tx_hash)

    account.sync_balances()
    assert account.wei_balance == 0
    assert (
        web3.eth.getBalance(faucet_address) == faucet_wei +
        account_wei - 21000 * NETWORK_CFG.GAS_PRICE
    )
