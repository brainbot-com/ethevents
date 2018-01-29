import click
import gevent
from flask import Flask, request, Response
from flask_restful import Api, Resource
from flask_cors import CORS
from gevent import monkey
from gevent.pywsgi import WSGIServer

from requests import Session

import logging

from ethevents import App
from microraiden.utils import pop_function_kwargs

log = logging.getLogger(__name__)

monkey.patch_all(thread=False)


class Forwarder(Resource):
    def __init__(self, session: Session, base_url='http://localhost'):
        self.session = session
        self.base_url = base_url

    def default(self, *args, **kwargs):
        data = request.get_data()
        url = self.base_url + request.path
        log.debug('{} {} {}'.format(url, data, request.headers))
        # sanitize headers (Host and Accept confuse the remote)
        headers = {key: request.headers.get(key) for key in request.headers.keys()}
        headers.pop('Host')
        if 'Accept' in headers.keys():
            headers.pop('Accept')
        response = self.session.request(
            request.method,
            url.strip('/'),
            params=request.query_string or None,
            data=data,
            headers=headers,
            timeout=30,
        )
        forwarded_headers = {
            header: value for header, value in response.headers.items()
            if 'content-length' not in header.lower()
        }
        content = response.text
        log.debug('content {}'.format(content))
        log.info('headers {}'.format(response.headers))
        return Response(
            content,
            mimetype=forwarded_headers.get('Content-type'),
            status=response.status_code,
            headers=forwarded_headers
        )

    def get(self, *args, **kwargs):
        return self.default(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.default(*args, **kwargs)


def run_proxy(
        client_app: App = None,
        endpoint_url: str = 'https://api.eth.events',
        proxy_listen_address: str = 'localhost',
        proxy_port: int = 5478,
        corsdomain=None,
        **kwargs
):
    if client_app is None:
        ctor_kwargs = pop_function_kwargs(kwargs, App.__init__)
        start_kwargs = pop_function_kwargs(kwargs, App.start)
        start_kwargs['endpoint_url'] = endpoint_url

        client_app = App(**ctor_kwargs)
        client_app.start(**start_kwargs)
        if not client_app.account.unlocked:
            return None, None, None

    app = Flask(__name__)

    app.url_map.strict_slashes = False

    api = Api(app)

    api.add_resource(
        Forwarder,
        '/<part1>',
        '/<part1>/<part2>',
        '/<part1>/<part2>/<part3>',
        resource_class_kwargs=dict(
            session=client_app.session,
            base_url=endpoint_url
        )
    )
    if corsdomain is not None:
        cors_enabled = CORS(app, resources={'/*': {"origins": corsdomain}})
        log.info('CORS was enabled for {}'.format(cors_enabled))

    print('Starting eth.events proxy server.')
    server = WSGIServer((proxy_listen_address, proxy_port), app)
    server_greenlet = gevent.spawn(server.serve_forever)

    return server, server_greenlet, client_app


@click.option(
    '--limits/--no-limits',
    default=True
)
@click.command()
def main(limits: bool):
    proxy, proxy_greenlet = run_proxy(
        endpoint_url='https://api.eth.events',
        ignore_security_limits=not limits
    )
    if proxy is None:
        return
    proxy_greenlet.join()


def entrypoint():
    logging.basicConfig(level=logging.DEBUG, filename='/tmp/log.txt')
    main()


if __name__ == '__main__':
    entrypoint()
