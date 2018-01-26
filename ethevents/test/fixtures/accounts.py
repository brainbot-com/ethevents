import json
from itertools import cycle
from typing import List
from datetime import datetime, timedelta

import os

import pytest
from eth_utils import decode_hex
from eth_keyfile import create_keyfile_json

from ethevents.account_manager import keyfile_name
from ethevents.types import PrivateKeyHex, Address, KeyfileContent
from microraiden.utils import privkey_to_addr


@pytest.fixture(scope='session')
def num_accounts() -> int:
    return 10


@pytest.fixture(scope='session')
def addresses(private_keys: List[PrivateKeyHex]) -> List[Address]:
    return [privkey_to_addr(private_key) for private_key in private_keys]


@pytest.fixture(scope='session')
def passwords(num_accounts: int) -> List[str]:
    words = 'enhance square skin area odor push pizza eagle assault stove usage morning sport ' \
            'call already shoulder similar truck violin rookie estate trophy coil raise'
    words_cycle = cycle(words.split())
    return [next(words_cycle) for i in range(num_accounts)]


@pytest.fixture(scope='session')
def keyfile_contents(
        private_keys: List[PrivateKeyHex],
        passwords: List[str]
) -> List[KeyfileContent]:
    return [
        create_keyfile_json(decode_hex(private_key), password.encode(), iterations=1000)
        for private_key, password in zip(private_keys, passwords)
    ]


@pytest.fixture
def keystore_path(tmpdir) -> str:
    return tmpdir.mkdir('keystore').strpath


@pytest.fixture
def keyfile_paths(
        keystore_path: str,
        private_keys: List[PrivateKeyHex],
        keyfile_contents: List[KeyfileContent]
) -> List[str]:
    keyfile_paths = []
    start_time = datetime.utcnow()
    start_time = start_time - timedelta(days=10)
    for i, (private_key, keyfile_content) in enumerate(zip(private_keys, keyfile_contents)):
        keyfile_paths.append(os.path.join(keystore_path, keyfile_name(
            keyfile_content['address'],
            time=start_time + timedelta(days=i)
        )))
    return keyfile_paths


@pytest.fixture
def keyfiles(keyfile_paths: List[str], keyfile_contents: List[KeyfileContent]) -> None:
    for keyfile_path, keyfile_content in zip(keyfile_paths, keyfile_contents):
        with open(keyfile_path, 'w') as keyfile:
            json.dump(keyfile_content, keyfile)
