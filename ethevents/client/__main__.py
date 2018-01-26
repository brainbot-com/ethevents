import click
import IPython

import elasticsearch

from ethevents.client.app import App
from ethevents.client.connection import MicroRaidenTransport


@click.option(
    '--logfile',
    type=click.Path(dir_okay=False, resolve_path=True),
    default='ethevents.log'
)
@click.option(
    '--limits/--no-limits',
    default=True
)
@click.command()
def main(logfile: str, limits: bool):
    import logging
    logging.basicConfig(level=logging.INFO, filename=logfile)
    logging.getLogger('urllib3').setLevel(logging.DEBUG)
    logging.getLogger('blockchain').setLevel(logging.DEBUG)
    logging.getLogger('channel_manager').setLevel(logging.DEBUG)
    logging.getLogger('ethevents').setLevel(logging.DEBUG)

    app = App()
    app.start(ignore_security_limits=not limits, endpoint_url='https://api.eth.events:433')

    if app.account.unlocked:
        es = elasticsearch.Elasticsearch(
            transport_class=MicroRaidenTransport,
            hosts=['api.eth.events:443'],
            use_ssl=True,
            session=app.session,
            timeout=30,
        )

        IPython.start_ipython(
            user_ns=dict(es=es),
            argv=[],
        )


if __name__ == '__main__':
    main()
