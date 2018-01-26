import time

import click
import requests
from elasticsearch.connection import Connection
from elasticsearch.connection_pool import DummyConnectionPool
from elasticsearch.transport import Transport
from elasticsearch.exceptions import (
    ConnectionError,
    ConnectionTimeout,
    SSLError
)
from elasticsearch.compat import urlencode
from requests import Session
from ethevents.client.app import App

import logging

log = logging.getLogger(__name__)


class MicroRaidenConnection(Connection):

    def __init__(
        self,
        host,
        port,
        session: Session,
        use_ssl=False,
        headers=None,
        **kwargs
    ):
        super(MicroRaidenConnection, self).__init__(
            host=host,
            port=port,
            use_ssl=use_ssl,
            **kwargs
        )
        self.base_url = 'http%s://%s:%d%s' % (
                        's' if self.use_ssl else '',
                        host, port, self.url_prefix
        )
        self.session = session
        self.session.headers = headers or {}
        self.session.headers.setdefault('content-type', 'application/json')

    def perform_request(
        self,
        method,
        url,
        params=None,
        body=None,
        timeout=None,
        ignore=(),
        headers=None
    ):
        url = self.base_url + url
        if params:
            url = '%s?%s' % (url, urlencode(params or {}))

        start = time.time()
        request = requests.Request(method=method, headers=headers, url=url, data=body)
        prepared_request = self.session.prepare_request(request)
        settings = self.session.merge_environment_settings(
            prepared_request.url,
            {},
            None,
            None,
            None
        )
        send_kwargs = {'timeout': timeout or self.timeout}
        send_kwargs.update(settings)
        try:
            response = self.session.request(
                prepared_request.method,
                prepared_request.url,
                data=prepared_request.body,
                headers=prepared_request.headers,
                **send_kwargs
            )
            duration = time.time() - start
            raw_data = response.text
        except Exception as e:
            self.log_request_fail(
                method,
                url,
                prepared_request.path_url,
                body,
                time.time() - start,
                exception=e
            )
            if isinstance(e, requests.exceptions.SSLError):
                raise SSLError('N/A', str(e), e)
            if isinstance(e, requests.Timeout):
                raise ConnectionTimeout('TIMEOUT', str(e), e)
            raise ConnectionError('N/A', str(e), e)

        # raise errors based on http status codes, let the client handle those if needed
        if not (200 <= response.status_code < 300) and response.status_code not in ignore:
            self.log_request_fail(
                method,
                url,
                response.request.path_url,
                body,
                duration,
                response.status_code,
                raw_data
            )
            self._raise_error(response.status_code, raw_data)

        self.log_request_success(
            method,
            url,
            response.request.path_url,
            body,
            response.status_code,
            raw_data,
            duration
        )

        return response.status_code, response.headers, raw_data


class MicroRaidenTransport(Transport):
    def __init__(
        self,
        hosts,
        *args,
        session: Session,
        connection_class=MicroRaidenConnection,
        connection_pool_class=DummyConnectionPool,
        **kwargs
    ):
        self.hosts = hosts
        log.debug('initializing transport')
        super(MicroRaidenTransport, self).__init__(
            hosts,
            *args,
            connection_class=connection_class,
            connection_pool_class=connection_pool_class,
            session=session,
            **kwargs
        )


@click.option(
    '--limits/--no-limits',
    default=True
)
@click.command()
def main(limits: bool):
    logging.basicConfig(level=logging.DEBUG)
    log.debug('in main')
    app = App()
    app.start(ignore_security_limits=not limits, endpoint_url='https://api.eth.events')
    log.debug('session started')

    if app.account.unlocked:
        import elasticsearch
        es = elasticsearch.Elasticsearch(
            transport_class=MicroRaidenTransport,
            hosts=['api.eth.events:443'],
            use_ssl=True,
            session=app.session
        )
        response = es.search('ethereum', 'block', body=dict(query=dict(match_all=dict())))
        print(response)


if __name__ == '__main__':
    main()
