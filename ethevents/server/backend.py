import logging
import json

import time
from collections import namedtuple

from flask import abort
from gevent.event import AsyncResult

from ethevents.config import (
    ETH_INDEX,
    LOG,
    BLOCK,
    TX,
)

Resource = namedtuple('Resource', ['content', 'price', 'expires_at'])

log = logging.getLogger(__name__)

ONLY_BLOCK = dict(
    index=ETH_INDEX,
    doc_type=BLOCK,
)

ONLY_TX = dict(
    index=ETH_INDEX,
    doc_type=TX,
)

ONLY_LOG = dict(
    index=ETH_INDEX,
    doc_type=LOG,
)


class ESCostCollector(object):

    def __init__(self):
        self.accumulated = 0
        self.price = AsyncResult()

    def add(self, result):
        self.accumulated += result['took']

    def finalize(self):
        self.price.set(self.accumulated)

    def get_price(self):
        return self.price.get()


def filtered_query(must=None, filter=None, should=None, must_not=None):
    return {
        "query": {
            "bool": {
                "must": must or {},
                "filter": filter or {},
                "should": should or {},
                "must_not": must_not or {}
            }
        }
    }


def sanitize(kwargs):
    result = dict()
    for key, value in kwargs.items():
        if key == 'index':
            if value not in ('ethereum', 'abi'):
                result[key] = 'ethereum'
            else:
                result[key] = value
        elif key == 'body':
            body_content = json.dumps(value)
            if 'script' in body_content and 'lang' in body_content:
                abort(405)
            result['body'] = value
        else:
            result[key] = value
    return result


class ElasticsearchBackend(object):
    def __init__(self, es, result_ttl: float = 30):
        self.es = es
        self.result_ttl = result_ttl

    def search(self, **kwargs) -> Resource:
        search_kwargs = sanitize(kwargs)
        collector = ESCostCollector()
        response = self.es.search(**search_kwargs)
        collector.add(response)
        collector.finalize()
        result = Resource(
            content=response,
            price=collector.get_price(),
            expires_at=time.time() + self.result_ttl
        )
        assert isinstance(result, Resource)
        return result

    def msearch(self, **kwargs) -> Resource:
        new_body = []
        if 'body' in kwargs:
            body = kwargs.pop('body')
            body = body.decode('utf-8')
            for search in body.strip().split('\n'):
                new_body.append(json.dumps(sanitize(json.loads(search))))
        other_kwargs = sanitize(kwargs)
        collector = ESCostCollector()
        multi_response = self.es.msearch(body=new_body, **other_kwargs)
        for response in multi_response['responses']:
            collector.add(response)
        collector.finalize()
        result = Resource(
            content=multi_response,
            price=collector.get_price(),
            expires_at=time.time() + self.result_ttl
        )
        return result

    def get_mapping(self, **kwargs) -> Resource:
        response = self.es.indices.get_mapping(**kwargs)
        return Resource(
            content=response,
            price=5,
            expires_at=time.time() + 10 * self.result_ttl
        )
