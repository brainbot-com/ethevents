import time
from _pytest.monkeypatch import MonkeyPatch
from elasticsearch import Elasticsearch

from ethevents import App
from ethevents.client.proxy import run_proxy
from ethevents.server.api_server import APIServer
from ethevents.server.backend import ElasticsearchBackend, Resource


def test_proxy(
        monkeypatch: MonkeyPatch,
        api_server: APIServer,
        initialized_client_app: App,
        api_endpoint_address: str
):
    app = initialized_client_app

    def search_patched(*args, **kwargs):
        return Resource({'something': 1}, 5, time.time() + 30)

    monkeypatch.setattr(ElasticsearchBackend, 'search', search_patched)

    proxy, proxy_greenlet, _ = run_proxy(
        client_app=app,
        endpoint_url='http://' + api_endpoint_address
    )

    es = Elasticsearch(hosts=['http://localhost:5478'])

    result = es.search(index='ethereum', body={'getme': 'anything'})
    assert result['something'] == 1

    proxy.stop()
    proxy_greenlet.join()
