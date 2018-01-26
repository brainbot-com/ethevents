import time
from _pytest.monkeypatch import MonkeyPatch
from elasticsearch import Elasticsearch

from ethevents import App
from ethevents.client.connection import MicroRaidenTransport
from ethevents.server.api_server import APIServer
from ethevents.server.backend import ElasticsearchBackend, Resource


def test_connection(
        monkeypatch: MonkeyPatch,
        api_server: APIServer,
        initialized_client_app: App,
        api_endpoint_address: str
):
    def search_patched(*args, **kwargs):
        return Resource('something', 5, time.time() + 30)

    monkeypatch.setattr(ElasticsearchBackend, 'search', search_patched)
    es = Elasticsearch(
        transport_class=MicroRaidenTransport,
        hosts=[api_endpoint_address],
        session=initialized_client_app.session
    )

    result = es.search(index='ethereum', body={'getme': 'anything'})
    assert result == 'something'
