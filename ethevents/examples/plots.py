import click
from datetime import datetime

import os

from elasticsearch import Elasticsearch

from ethevents.client.proxy import run_proxy
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


def plot_gas_usage(es: Elasticsearch):
    body = {
        'aggs': {
            'half_hour': {
                'aggs': {'used_gas': {'avg': {'field': 'gasUsed.num'}}},
                'date_histogram': {
                    'field': 'timestamp',
                    'interval': '30m',
                    'min_doc_count': 0
                }
            }
        },
        'query': {
            'bool': {
                'filter': [{
                    'range': {
                        'timestamp': {
                            'gte': 'now/d-7d',
                            'lte': 'now/d-1d'
                        }
                    }
                }]
            }
        },
        'size': 0
    }

    response = es.search(index='ethereum', body=body)
    data = response['aggregations']['half_hour']['buckets']

    x = [datetime.fromtimestamp(bucket['key'] / 1000) for bucket in data]
    y = [bucket['used_gas']['value'] for bucket in data]

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(15, 6)
    ax.yaxis.set_major_formatter(mtick.EngFormatter())
    ax.set_xlabel('Date')
    ax.set_ylabel('Gas Usage')
    ax.plot(x, y)
    fig.autofmt_xdate()

    os.makedirs('plots', exist_ok=True)
    fig.savefig('plots/gas_usage_{}.png'.format(datetime.now().isoformat()), bbox_inches='tight')

    plt.show()


@click.option(
    '--limits/--no-limits',
    default=True
)
@click.command()
def main(limits: bool):
    proxy, proxy_greenlet, app = run_proxy(
        ignore_security_limits=not limits,
        endpoint_url='https://api.eth.events'
    )

    if app.account.unlocked and proxy is not None:
        es = Elasticsearch(hosts=['http://localhost:5478'])
        plot_gas_usage(es)

    proxy.stop()
    proxy_greenlet.join(timeout=5)


if __name__ == '__main__':
    main()
