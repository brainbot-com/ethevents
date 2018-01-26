import os

import click

API_URL = 'https://api.eth.events'
APP_DIR = 'eth.events'
KEYSTORE_DIR = 'keystore'
TOKEN_SYMBOL = 'RDN'
TOKEN_DECIMALS = 18

KEYSTORE_PATH = os.path.join(click.get_app_dir(APP_DIR), KEYSTORE_DIR)
WEI_THRESHOLD = 2 * 10 ** 13
WEI_LIMIT = 2 * 10 ** 18
REI_THRESHOLD = 10 ** 5
REI_LIMIT = 3 * 10 ** 18

# Number of iterations for the password-derived encryption key derivation. Default is 100,000.
PASSWORD_ITERATIONS = 10000

# number of blocks we assume required for finality
INDEXING_REORG_SAFE = 6

ETH_INDEX = 'ethereum'
BLOCK = 'block'
TX = 'tx'
LOG = 'log'
