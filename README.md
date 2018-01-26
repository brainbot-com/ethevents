# ethevents
eth.events client and server library

eth.events is a search index for the Ethereum blockchain. The blockchain data is indexed with
Elasticsearch. The server part of eth.events exposes an API that can execute queries written with
the [Elasticsearch Query-DSL](https://www.elastic.co/guide/en/elasticsearch/reference/5.6/query-dsl.html).
Users can execute arbitrary queries against this API, however they will need to pay for each request
with [Microraiden](https://github.com/raiden-network/microraiden) payments.

The remainder of the README will focus on the user side / client library of the software.

## Requirements
Installation needs `python3`.

Runtime needs an Ethereum blockchain client with `rpc` enabled.

## Installation
Clone this repository and run

    cd ethevents && virtualenv .venv && source .venv/bin/activate && pip install .

## First start
Run

    ethevents

to start the client.

Upon first start, `ethevents` will create a hot-wallet for the user. In order to connect to the
API, that newly created hot-wallet will require funding. A small amount of ETH for opening and
closing channels (maximum 2.0 ETH) and some RDN tokens for paying actual requests. 

There is an RDN vending machine at **FIXME** that can be used to acquire RDN tokens.

Requests to the search index will cost `1 REI` per millisecond of the `took` portion of the Elasticsearch
response. If the request took `3153 ms`, the price will be `3153 REI` or `3.153e-15` RDN.

## Using the client
There are two ways to use the client, through a prepopulated ipython REPL and by connecting to the
local proxy server.

### Using the ipython REPL
After starting the client with

    ethevents

and unlocking the hot-wallet, an ipython REPL is started, prepopulated with some objects necessary
for interacting with the blockchain index. For simplified discoverability, all prepopulated objects
are mirrored in the `ee.` namespace, so typing `ee.` and hitting `<TAB>` will give insight into
the available objects. For brevity, the following will use the user objects with their shorthand
(i.e. without the `ee.` prefix).

#### Searching the blockchain index
The `es` object is an [`elasticsearch-py`](https://github.com/elastic/elasticsearch-py) instance,
that will automatically pay for any request via Microraiden payments.
Calling

    es.search('ethereum', 'block', body={})

will for example search for blocks in the index.
    
    es.indices.get_mapping('ethereum')

will return the configured index mapping for the Ethereum blockchain index.

The `queries` module contains a number of functions that generate example queries (see `ethevents/examples/queries.py`).
They are meant as a quickstart helper for queries but they are in no way exhausting the space of
potential queries against the search index.

The ipython `?` operator is helpful to determine the available arguments for an example query, e.g.

    queries.caller_for_event?

will output:

    Signature: queries.caller_for_event(event_sig='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef', time_range={'gt': 0}, num_callers=10)
    Docstring:
    This query aggregates the most common caller addresses for all transactions
    that lead to a certain `event_sig` topic:
    - `caller` collects the `num_callers` most common sender addresses
    - `gasprice_stats` aggregates gas price statistics per caller

    Usage:
        es.search('ethereum', 'tx', body=caller_for_event())

    Params:
        event_sig (str): an event signature (topics[0])
        time_range (dict): a range query dictionary for the `timestamp` field (default: all time)
        num_callers (int): number of top caller addresses to return
    Returns:
        query (dict): an elasticsearch query body dictionary.

Calling

    es.search('ethereum', 'tx', body=queries.caller_for_event(time_range=dict(gt='now/h - 1h')))

will for example aggregate the ten most common account addresses that generated an ERC20 transfer
event in the last hour (opposed to the default value, "since all time", `'gt': 0`).

Please refer to the elasticsearch documentation if you want to learn more about the Query DSL.

### Using the proxy server
Once the client is running, it exposes a forward proxy at http://localhost:5478 to the Elasticsearch
API. The supported API endpoints are

    POST /ethereum/<_type>/_search
    POST /_msearch
    GET /ethereum/<_type>/_mapping

Any Elasticsearch consumer API that is satisified with these endpoints can be connected to this
proxy.

The client proxy implementation will automatically forward, **and pay for**, requests to the blockchain
index.

