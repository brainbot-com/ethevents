import json
from typing import List

import gevent
import mock
import requests
import time

from _pytest.monkeypatch import MonkeyPatch
from eth_utils import encode_hex
from flask import Request
from munch import Munch
from web3 import Web3

from ethevents.server.backend import ElasticsearchBackend, Resource
from microraiden import HTTPHeaders, Client, Session as uSession
from microraiden.proxy.paywalled_proxy import PaywalledProxy
import microraiden.requests
from ethevents.server.api_server import APIServer, ExpensiveElasticsearch


def test_get(
        empty_proxy: PaywalledProxy,
        api_endpoint_address: str,
        channel_manager_address: str,
        token_address: str,
        sender_address: str,
        receiver_address: str,
        client: Client,
        wait_for_blocks
):
    """
    Test with manual client interaction for isolated server testing.
    Note: Debug in microraiden.proxy.resources.expensive for most of the server response logic.
    """
    es_mock = ElasticsearchBackend(None)
    es_mock.search = mock.Mock(return_value=Resource(
        price=5,
        content='success',
        expires_at=time.time() + 30
    ))
    server = APIServer(empty_proxy, es=es_mock)
    api_path = 'http://' + api_endpoint_address

    # Request price (and cache resource).
    body = {'query': 'query something'}
    url = api_path + '/some_index/some_type/_search'
    response = requests.get(url, json=body)

    print(response.content)
    assert response.status_code == 402

    headers = HTTPHeaders.deserialize(response.headers)
    assert headers.token_address == token_address
    assert headers.contract_address == channel_manager_address
    assert headers.receiver_address == receiver_address
    price = int(headers.price)
    assert price == 5
    assert len(server.resource_cache) == 1

    # Perform payment and request same resource again. Include payment information in headers.
    channel = client.get_suitable_channel(receiver_address, price)
    # Server requires some confirmations, so mine some blocks.
    wait_for_blocks(10)
    channel.create_transfer(price)

    headers = Munch()
    headers.balance = str(channel.balance)
    headers.balance_signature = encode_hex(channel.balance_sig)
    headers.sender_address = sender_address
    headers.receiver_address = receiver_address
    headers.open_block = str(channel.block)
    headers = HTTPHeaders.serialize(headers)

    response = requests.get(url, headers=headers, json=body)
    headers = HTTPHeaders.deserialize(response.headers)

    assert 'nonexisting_channel' not in headers, 'Server should acknowledge the created channel.'
    assert 'insuf_confs' not in headers, 'Server should acknowledge the created channel.'
    assert 'invalid_amount' not in headers, 'The correct amount should have been sent.'
    assert response.status_code == 200
    assert response.json() == 'success'
    assert len(server.resource_cache) == 1

    es_mock.search.assert_called_once_with(
        index='some_index',
        doc_type='some_type',
        body={'query': 'query something'}
    )


def test_get_microraiden(
        monkeypatch: MonkeyPatch,
        wait_for_blocks,
        empty_proxy: PaywalledProxy,
        api_endpoint_address: str,
        private_keys: List[str],
        web3: Web3,
        channel_manager_address: str,
):
    es_mock = ElasticsearchBackend(None)
    es_mock.search = mock.Mock(return_value=Resource(
        price=5,
        content='success',
        expires_at=time.time() + 30
    ))

    def on_nonexisting_channel_patched(*args, **kwargs):
        wait_for_blocks(6)
        return True

    monkeypatch.setattr(
        microraiden.client.session.Session,
        'on_nonexisting_channel',
        on_nonexisting_channel_patched
    )

    APIServer(empty_proxy, es=es_mock)
    api_path = 'http://' + api_endpoint_address

    body = {'query': 'query something'}
    url = api_path + '/some_index/some_type/_search'
    response = microraiden.requests.get(
        url,
        json=body,
        private_key=private_keys[0],
        web3=web3,
        channel_manager_address=channel_manager_address
    )

    assert response
    assert response.status_code == 200
    assert response.json() == 'success'

    es_mock.search.assert_called_once_with(
        index='some_index',
        doc_type='some_type',
        body={'query': 'query something'}
    )


def test_get_expired(
        empty_proxy: PaywalledProxy,
        api_endpoint_address: str,
        sender_address: str,
        receiver_address: str,
        client: Client,
        wait_for_blocks
):
    """
    Test with manual client interaction for isolated server testing.
    Note: Debug in microraiden.proxy.resources.expensive for most of the server response logic.
    """
    es_mock = ElasticsearchBackend(None)
    es_mock.search = mock.Mock(return_value=Resource(
        price=5,
        content='success',
        expires_at=time.time() + 0.05
    ))
    APIServer(empty_proxy, es=es_mock)
    api_path = 'http://' + api_endpoint_address

    # Request price (and cache resource).
    body = {'query': 'query something'}
    url = api_path + '/some_index/some_type/_search'
    response = requests.get(url, json=body)
    assert response.status_code == 402

    # Perform payment and request same resource again. Include payment information in headers.
    channel = client.get_suitable_channel(receiver_address, 5)
    # Server requires some confirmations, so mine some blocks.
    wait_for_blocks(10)
    channel.create_transfer(5)

    headers = Munch()
    headers.balance = str(channel.balance)
    headers.balance_signature = encode_hex(channel.balance_sig)
    headers.sender_address = sender_address
    headers.receiver_address = receiver_address
    headers.open_block = str(channel.block)
    headers = HTTPHeaders.serialize(headers)

    # Make sure the price changes for the next request.
    es_mock.search = mock.Mock(return_value=Resource(
        price=3,
        content='success',
        expires_at=time.time() + 0.05
    ))
    # Let former query expire.
    gevent.sleep(0.1)

    # Query same resource again with the old expired price.
    response = requests.get(url, headers=headers, json=body)

    assert response.status_code == 402
    assert response.headers[HTTPHeaders.PRICE] == '3'

    channel.update_balance(3)
    headers[HTTPHeaders.BALANCE] = str(channel.balance)
    headers[HTTPHeaders.BALANCE_SIGNATURE] = encode_hex(channel.balance_sig)

    response = requests.get(url, headers=headers, json=body)

    assert response.json() == 'success'

    es_mock.search.call_args_list == [
        {'query': 'query something'},
        {'query': 'query something'}
    ]


def test_request_hashing():
    get = Request.from_values(method='GET', path='/somepath')
    get_key = ExpensiveElasticsearch.get_request_key(get)
    assert get_key
    get2 = Request.from_values(method='get', path='/somepath')
    get2_key = ExpensiveElasticsearch.get_request_key(get2)
    assert get_key == get2_key

    post = Request.from_values(
        method='POST',
        path='/somepath',
        content_type='application/json',
        data=json.dumps(dict(a=1, b='value', c=dict(c=3, x=4)))
    )
    post_key = ExpensiveElasticsearch.get_request_key(post)
    assert post_key
    post2 = Request.from_values(
        method='POST',
        path='/somepath',
        content_type='application/json',
        data=json.dumps(dict(a=1, b='value', c=dict(c=3, x=4)))
    )
    post2_key = ExpensiveElasticsearch.get_request_key(post2)
    assert post_key == post2_key


def test_cache_cleanup(
        empty_proxy: PaywalledProxy,
        usession: uSession,
        api_endpoint_address: str
):
    now = time.time()
    es_mock = ElasticsearchBackend(None)

    api_path = 'http://' + api_endpoint_address
    resource_url = '/some_index/some_type/_search'
    url = api_path + resource_url

    bodies = [
        {'query': 'query something'},
        {'query': 'query some other thing'},
        {'query': 'query some third thing'},
    ]
    requests = [
        Request.from_values(
            method='GET',
            base_url=api_path,
            path=resource_url,
            content_type='application/json',
            data=json.dumps(bodies[0])
        ),
        Request.from_values(
            method='GET',
            base_url=api_path,
            path=resource_url,
            content_type='application/json',
            data=json.dumps(bodies[1])
        ),
        Request.from_values(
            method='GET',
            base_url=api_path,
            path=resource_url,
            content_type='application/json',
            data=json.dumps(bodies[2])
        )
    ]
    resources = [
        Resource(content='success1', price=4, expires_at=now - 100),
        Resource(content='success2', price=4, expires_at=now + 100),
        Resource(content='success3', price=4, expires_at=now - 100),
    ]
    es_mock.search = mock.Mock(return_value=resources[1])

    server = APIServer(empty_proxy, es=es_mock)
    server.resource_cache.update({
        ExpensiveElasticsearch.get_request_key(requests[0]): resources[0],
        ExpensiveElasticsearch.get_request_key(requests[1]): resources[1],
        ExpensiveElasticsearch.get_request_key(requests[2]): resources[2]
    })
    assert len(server.resource_cache) == 3

    response = usession.get(url, json=bodies[1])
    assert response.json() == 'success2'
    assert len(server.resource_cache) == 1
