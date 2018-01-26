import os
import sys
import click

from microraiden.click_helpers import main, pass_app
from microraiden.proxy.paywalled_proxy import PaywalledProxy

from elasticsearch import Elasticsearch

from ethevents.server.api_server import APIServer
from ethevents.server.backend import ElasticsearchBackend

import logging


@main.command()
@click.option(
    '--host',
    default='0.0.0.0',
    help='Address of the proxy'
)
@click.option(
    '--port',
    default=5000,
    help='Port of the proxy'
)
@click.option(
    '--elasticsearch',
    default='https://es1.eth.events',
)
@pass_app
def start(app: PaywalledProxy, host: str, port: int, elasticsearch: str):
    auth = os.environ.get('ES_CREDENTIALS')
    if auth is None:
        print('Please provide elasticsearch credentials via ES_CREDENTIALS environment.')
        sys.exit(1)
    elasticsearch_connection = Elasticsearch(elasticsearch, timeout=30, http_auth=auth)
    backend = ElasticsearchBackend(elasticsearch_connection)
    APIServer(app, backend)
    app.run(host=host, port=port, debug=True)
    app.join()


if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_all()
    logging.basicConfig(
        level=logging.DEBUG,
        filename='/tmp/server.log',
        format='%(asctime)s %(levelname)s %(message)s'
    )
    main()
