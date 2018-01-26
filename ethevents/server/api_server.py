import time
from typing import Dict

from flask import request, abort
from flask import jsonify
from gevent.threading import Lock

from microraiden.proxy.resources.expensive import Expensive
from microraiden.proxy.paywalled_proxy import PaywalledProxy
from .backend import ElasticsearchBackend, Resource

import logging

log = logging.getLogger(__name__)


class ExpensiveElasticsearch(Expensive):
    def __init__(
            self,
            resource_cache: Dict[int, Resource],
            cache_lock: Lock,
            es: ElasticsearchBackend,
            *args,
            **kwargs
    ):
        self.resource_cache = resource_cache
        self.cache_lock = cache_lock
        self.es = es
        Expensive.__init__(self, *args, **kwargs)

    @staticmethod
    def get_request_key(request: request) -> int:
        # FIXME: this assumes that serialized json data doesn't change order between requests
        # it's a compromise to make NDJSON _msearch requests work (otherwise we could
        # explicitely dump json with `sort_keys=True`.
        data = request.get_data()
        request_key = hash((
            request.method.lower(),
            request.url.lower(),
            data
        ))
        return request_key

    def fetch_resource(self, request_key: int, _index: str, _type: str) -> Resource:
        resource = self.resource_cache.get(request_key)

        if resource is not None and resource.expires_at < time.time():
            self.cache_lock.acquire()
            self.resource_cache.pop(request_key)
            self.cache_lock.release()
            resource = None

        if resource is None:
            other_args = {key: request.values.get(key) for key in request.values.keys()}
            api_endpoint = request.path.split('/')[-1]
            if api_endpoint == '_search':
                resource = self.es.search(
                    index=_index,
                    doc_type=_type,
                    body=request.json,
                    **other_args
                )
            elif api_endpoint == '_mapping':
                resource = self.es.get_mapping(
                    index=_index,
                    doc_type=_type
                )
            elif api_endpoint == '_msearch':
                data = request.get_data()
                resource = self.es.msearch(
                    index=_index,
                    doc_type=_type,
                    body=data,
                    **other_args,
                )
            self.resource_cache[request_key] = resource

        return resource

    def price(self) -> int:
        """
        Request the resource price by querying the resource itself and caching it for later
        successful payments. If the resource is already cached, the price is read from the cache.
        """
        assert request is not None

        if request.method == 'GET':
            return self.price_get(**request.view_args)
        elif request.method == 'POST':
            return self.price_post(**request.view_args)
        else:
            raise ValueError('Method {} not allowed.'.format(request.method))

    def price_get(self, _index: str = None, _type: str = None):
        request_key = ExpensiveElasticsearch.get_request_key(request)

        return self.fetch_resource(request_key, _index, _type).price

    def price_post(self, _index: str = None, _type: str = None):
        return self.price_get(_index, _type)

    def get_resource_cached(self):
        # Price was just checked moments ago, so ignore expiry here.
        request_key = self.get_request_key(request)
        resource = self.resource_cache.get(request_key)

        # FIXME: there is a very rare edge case in which multiple concurrent requests to the same
        # resource might lead to the resource being deleted between the final price check and the
        # cache access.
        if resource is None:
            # Cache miss => 409 Conflict because bad code.
            abort(409)

        self.clean_cache()
        return resource

    def get(self, url: str, _index: str = None, _type: str = None):
        resource = self.get_resource_cached()
        return jsonify(resource.content)

    def post(self, url: str, _index: str = None, _type: str = None):
        resource = self.get_resource_cached()
        return jsonify(resource.content)

    def put(self, *args):
        return 'PUT not allowed', 405

    def delete(self, *args):
        return 'DELETE not allowed', 405

    def clean_cache(self):
        self.cache_lock.acquire()
        now = time.time()
        expired_resource_keys = [
            key for key, resource in self.resource_cache.items()
            if resource.expires_at < now
        ]
        for expired_resource_key in expired_resource_keys:
            del self.resource_cache[expired_resource_key]
        self.cache_lock.release()


class APIServer(object):
    def __init__(self, proxy: PaywalledProxy, es: ElasticsearchBackend):
        self.proxy = proxy
        self.resource_cache = {}
        self.cache_lock = Lock()
        proxy.add_paywalled_resource(
            ExpensiveElasticsearch,
            '/_search',
            None,
            '/<string:_index>/_search',
            '/<string:_index>/<string:_type>/_search',
            '/_msearch',
            '/<string:_index>/_msearch',
            '/<string:_index>/<string:_type>/_msearch',
            '/_mapping',
            '/<string:_index>/_mapping',
            '/<string:_index>/<string:_type>/_mapping',
            resource_class_kwargs=dict(
                resource_cache=self.resource_cache,
                cache_lock=self.cache_lock,
                es=es,
            )
        )
