Simple contract event query
===========================

Welcome!
--------

Within this tutorial you will learn how to retrieve and analyze data
from the Ethereum Blockchain with the help of the eth.events API.

We will show you how to retrieve data from eth.events using the
`ElasticSearch Query
DSL <https://www.elastic.co/guide/en/elasticsearch/reference/5.6/query-dsl.html>`__.

You will learn
~~~~~~~~~~~~~~

-  How to access eth.events
-  How to use different methods to query the eth.events API
-  How to write a basic query returning some events
-  How a return object is structured and which data it returns
-  How to filter events for a specific contract or a specific event type
-  How to sort the events by blocknumber

What you must know already
--------------------------

This tutorial is written for programmers, who have some experience with
JSON, Rest-APIs and the basic structure of HTTP-requests.

What you need
-------------

If you want play around with the HTTP-requests, you should install an
HTTP client. For pretty-printed responses in the terminal, we
recommend using `HTTPie <https://httpie.org/#installation>`__. For
advanced usage and a graphical UI we recommend using
`Postman <https://www.getpostman.com/apps>`__. We provide
copy-pasteable commands for ``HTTPie`` throughout the tutorial, so if you
want to follow along, it is advisable to install the software first.

Create an eth.events query step-by-step
---------------------------------------

Retrieve all events indexed by eth.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the eth.events endpoint ``/events/_search``, you are able to query
all events from the Ethereum mainnet.

A simple GET request to ``/ethereum/event/_search`` shows us 10 events in
no particular order.

 Execute the request with:

-  ``HTTPie``:

.. code:: bash

  http GET https://public.eth.events/ethereum/event/_search -a demouser:demouser

The returned JSON starts with meta-information about the processing of
the query (not shown here).

The query results are shown under the ``"hits"`` keyword in the
retrieved JSON data-structure:

.. code:: json

  "hits":{
    "total":69502921,
    "max_score":1,
    "hits":[
      ...
    ]
  }

You get the ``"total"`` number of hits. It represents the total number
of events in the eth.events index.

    The ``"max_score"`` isn't very interesting to us in general, because
    we mostly filter for boolean conditions, that can only be ``0`` (not
    returned by the query at all) or ``1``.

The actual events are listed under the ``hits.hits`` keyword. If we look
at one of the events, we can observe the general structure of an event.

.. code-block:: json

  {
    "_index":"ethereum_2",
    "_type":"event",
    "_id":"0x92c1b864051b9e6758ab217bc70e0d8641d5f830e16b0a7d15ba78ef2356ba9c_e_52",
    "_score":1,
    "_routing":"0x251d33d4ab03fb675bb2d09304a4aca28b943373c0bd8dbc85402d9e23f4f061",
    "_parent":"0x92c1b864051b9e6758ab217bc70e0d8641d5f830e16b0a7d15ba78ef2356ba9c",
    "_source":{
      "args":[
        {
          "name":"hash",
          "value.hex":"b'eb8dd23ef00be18cb4a263b4271e2f9c28bb47a239f179001691f6e887a6ed47'",
          "value.num":null,
          "value.scaled":null,
          "value.type":"bytes32",
          "pos":0
        },
        {
          "name":"registrationDate",
          "value.hex":"0x59948642",
          "value.num":1502905922,
          "value.type":"uint256",
          "pos":1,
          "value.scaled":null
        }
      ],
      "event":"AuctionStarted",
      "logIndex":{
        "num":52,
        "raw":"0x34"
      },
      "transactionIndex":{
        "num":92,
        "raw":"0x5c"
      },
      "transactionHash":"0x92c1b864051b9e6758ab217bc70e0d8641d5f830e16b0a7d15ba78ef2356ba9c",
      "address":"0x6090a6e47849629b7245dfa1ca21d94cd15878ef",
      "blockHash":"0x251d33d4ab03fb675bb2d09304a4aca28b943373c0bd8dbc85402d9e23f4f061",
      "blockNumber":{
        "num":4145267,
        "raw":"0x3f4073"
      },
      "error":null,
      "str":"AuctionStarted(b\"\\xeb\\x8d\\xd2>\\xf0\\x0b\\xe1\\x8c\\xb4\\xa2c\\xb4'\\x1e/\\x9c(\\xbbG\\xa29\\xf1y\\x00\\x16\\x91\\xf6\\xe8\\x87\\xa6\\xedG\", 1502905922)",
      "timestamp":"2017-08-11T17:52:02"
    }
  }


Again, we see meta information that is related to Elasticsearch
internals (not shown here).

We want to focus on the event fields, under the ``"_source"`` keyword:

- ``"event"`` - event name
- ``"blockNumber"`` - the block, where it was omitted
- ``"timestamp"`` - approximate timestamp, when it was included in the blockchain

Each argument of an event is an element in a list ``"args"``.

Filter events from a specific contract
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You are probably interested in filtering for events that belong to a
specific smart contract.

To demonstrate that, we will examine one of the
`DAI <https://makerdao.com/>`__'s ``DSToken`` contracts.

The contract for the DAI Stablecoin on the mainnet resides under the
address ``0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359``

The ``"address"`` field is where the originating contract address is
given. You will have to restrict the results with Elasticsearchs
filtering methods.

We don't want to use the very limited GET query. We will send a POST
request to eth.events, where we provide additional parameters in the
body of the HTTP-request:

.. code-block:: json

  {
    "query":{
      "bool":{
        "filter":{
          "term":{
            "address":"0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359"
          }
        }
      }
    }
  }


Execute the request with:

-  ``HTTPie``:

  .. code:: bash

    http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/erc20_contract.json | http POST https://public.eth.events/ethereum/event/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

  .. code:: bash

    curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/erc20_contract.json


The query has to be specified in the ``"query"`` parameter. We use a
`filter
context <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html#_scoring_with_literal_bool_filter_literal>`__
``"bool": {"filter": ...}`` because we are only interested in filtering
elements.

In the ``"term"`` parameter of the filter context, we require the
results to exactly match the specified value in the ``"address"``
argument of the event, namely the address of the DAI contract.

Filter for a specific type of event
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now every event under the ``hits.hits`` keyword originates from the
contract of interest. but there are still different types of events
present in the queries result.

The ``"event"`` field contains the name of the event, and if you look
through the results from the last query, you will most likely see 2
different types of events, ``Approval`` and ``Transfer``.

    *Note*: the feature of filtering by arguments and cleartext names of
    events is unique to eth.events and it's most outstanding feature.
    When using the usual ``web3`` interface, an event and it's values
    are encoded in a 64 byte hexstring. To decode the event to a human
    readable and easy to filter representation, the hexstring has to be
    decoded with the help of the ABI of the events contract.

    In eth.events, the events are already decoded and indexed for you!

The DAI contract is following the `ERC20 token
standard <https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md>`__.

From the DAI-Stablecoins ERC20 contracts code, we can see what events
are defined:

.. code-block:: js

    contract ERC20Events {
        event Approval(address indexed src, address indexed guy, uint wad);
        event Transfer(address indexed src, address indexed dst, uint wad);
    }

If we are interested in one type of event (``"Transfer"``), we have to
introduce another ``"term"`` filter, that gets appended to the
``"filter"`` list:


.. code-block:: json

  {
    "query":{
      "bool":{
        "filter":[
          {
            "term":{
              "event.keyword":"Transfer"
            }
          },
          {
            "term":{
              "address":"0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359"
            }
          }
        ]
      }
    }
  }



The ``”event”`` field defaults to a ``text`` type for full-text
searching. We want to match the event name exactly (case sensitive),
so we filter for the ``event.keyword`` field, which is of type
``keyword``. To learn more about the differences between ``text``
and ``keyword`` types in Elasticsearch, look
`here <https://www.elastic.co/guide/en/elasticsearch/reference/5.6/query-dsl-term-query.html>`__

Execute the request with:

-  ``HTTPie``:

  .. code:: bash

    http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/erc20_event_type.json | http POST https://public.eth.events/ethereum/event/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

  .. code:: bash

    curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/erc20_event_type.json

Retrieving sorted results
~~~~~~~~~~~~~~~~~~~~~~~~~

You may notice that the ``"timestamp"`` of the events is outdated and
that they are not sorted by their ``"blockNumber"``.

In order to change that, the query has to be modified again:

.. code-block:: json

  {
    "query":{
      "bool":{
        "filter":[
          {
            "term":{
              "event.keyword":"Transfer"
            }
          },
          {
            "term":{
              "address":"0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359"
            }
          }
        ]
      }
    },
    "sort":{
      "blockNumber.num":{
        "order":"desc"
      }
    },
    "size":5
  }

The ``"sort"`` parameter outside of the ``"query"`` nesting tells
eth.events which field should be used for sorting.

We specify the ``.num`` attribute of the ``blockNumber``, because we
want the integer representation and not a hex encoding.

With ``"order":"desc"``, the events will be sorted in descending order
of the block, where they were included in the blockchain.

Execute the request with:

-  ``HTTPie``:

  .. code:: bash

    http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/erc20_event_sorted.json | http POST https://public.eth.events/ethereum/event/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

  .. code:: bash

    curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/erc20_event_sorted.json

Restricting result size
~~~~~~~~~~~~~~~~~~~~~~~

In the last query we specified the ``"size"`` parameter with a value of
``5``. This will limit the number of retrieved events to 5. For testing
queries, it is advisable to set this to a small number.

With ``"size":-1``, all filtered results are retrieved from the server.
You will need to use this in conjunction with a carefully selected range
filter, for example a range of block-numbers.

Where to go from here
~~~~~~~~~~~~~~~~~~~~~

The best starting point is the `Elasticsearch
documentation <https://www.elastic.co/guide/en/elasticsearch/reference/5.6/query-dsl.html>`__.
There you’ll learn how to construct more complex filter queries or how
to combine filters with a boolean logic.

If you are not interested in single events, but rather on cumulated
properties and statistics, you should have a look at the various
possibilities of
`aggregations <https://www.elastic.co/guide/en/elasticsearch/reference/5.6/search-aggregations.html>`__.
The example queries at `http://eth.events <https://eth.events>`__ make
extensive use of aggregations and show how eth.events can be used to
plot various metrics of different smart contracts.
