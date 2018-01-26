import pytest

from ethevents.server.api_server import APIServer
from ethevents.server.backend import ElasticsearchBackend
from microraiden.proxy import PaywalledProxy


@pytest.fixture
def api_server(empty_proxy: PaywalledProxy):
    es_mock = ElasticsearchBackend(None)
    server = APIServer(empty_proxy, es_mock)
    return server
