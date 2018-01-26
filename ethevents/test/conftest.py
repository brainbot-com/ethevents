from microraiden.test.fixtures import *  # flake8: noqa
del globals()['session']
from microraiden.test.fixtures import session as usession  # flake8: noqa
from microraiden.test.conftest import pytest_addoption
from .fixtures import *  # flake8: noqa
from gevent import monkey

# Thread is false due to clash when testing both contract/microraiden modules.
monkey.patch_all(thread=False)
