Example queries
===============

The following queries are meant to be a building block for
your own eth.events queries.  


.. contents:: 
        :local: 


Block
~~~~~

Get block by blockhash
----------------------
The results will contain only the block with the given block `number`.
This requires no body.

.. code:: bash

    GET ethereum/block/0x4e3a3754410177e6937ef1f84bba68ea139e8d1a2258c5f85db9f1cd715a1bdd


Select by block number
----------------------

The results will contain only the block with the given block `number`.

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/block/_search

JSON body:

.. literalinclude:: block/by_blocknumber.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/block/by_blocknumber.json | http POST https://public.eth.events/ethereum/block/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/block/by_blocknumber.json


Filter empty blocks
-------------------

The results will contain only blocks that are empty (include no transactions).

HTTP-Method/Endpoint:

.. code:: bash

    POST /ethereum/block/_search

JSON body:

.. literalinclude:: block/empty_blocks.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/block/empty_blocks.json | http POST https://public.eth.events/ethereum/block/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/block/empty_blocks.json


Filter last 5 known blocks (sorted)
-----------------------------------

The results will only contain the 5 most recent blocks (highest block number) on the index.
Sorted in descending order (highest block number first).

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/block/_search

JSON body:

.. literalinclude:: block/last_5_sorted.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/block/last_5_sorted.json | http POST https://public.eth.events/ethereum/block/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/block/last_5_sorted.json


Transaction
~~~~~~~~~~~

Filter by the transaction's block's hash
----------------------------------------

The results will contain all transactions that are included in the 
specified block, identified with it's `blockHash`.

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/tx/_search

JSON body:

.. literalinclude:: tx/by_block_hash.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/tx/by_block_hash.json | http POST https://public.eth.events/ethereum/tx/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/tx/by_block_hash.json 

Filter by a range of block numbers
----------------------------------

The results will contain all transactions, that are included in 
a block, that is within the specified boundaries of the block number
range. The block number has to be greater than or equal to 4242 (`gte`)
and less than or equal to 5353 (`lte`).
The results will show a maximum of 200 blocks, in no particular order.


HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/tx/_search

JSON body:

.. literalinclude:: tx/by_blocknumber_range.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/tx/by_blocknumber_range.json | http POST https://public.eth.events/ethereum/tx/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/tx/by_blocknumber_range.json


Filter by receiving or originating address
------------------------------------------

The results will contain all transactions, whose sender (`from`) or receiver (`to`) is 
has the specified address.

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/tx/_search

JSON body:

.. literalinclude:: tx/by_from_or_to_address.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/tx/by_from_or_to_address.json | http POST https://public.eth.events/ethereum/tx/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/tx/by_from_or_to_address.json



Select by transaction hash
--------------------------

The results will contain only the transaction with the given transaction `hash`.

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/tx/_search

JSON body:

.. literalinclude:: tx/by_tx_hash.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/tx/by_tx_hash.json | http POST https://public.eth.events/ethereum/tx/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/tx/by_tx_hash.json


Create link for tx in block document
-------------------------------------

Given a block document

.. code:: json

    {
                    ...
                    "_type": "block",
                    "_id": "0x0077065fa4f03a4ab28ba52bca5b2d56b5f70de2f0dc06adbc586ada7e8a2f7a",
                    "_source": {
                        ...    
                        "transactions": [
                            "0xc7b58c58a019479107d93941d044a9ffa9873c41437458eedcf889efe25738b8",
                            "0x14829930e553466a27fabea994e71420333dfa2f3214e0e148ce49b427191dac",
                            ...
                        ],
                        ...
                    }
                }

you can GET any of the enclosed tx via this link

.. code:: bash

    GET ethereum/tx/0xc7b58c58a019479107d93941d044a9ffa9873c41437458eedcf889efe25738b8?routing=0x0

Log
~~~

Filter by causing transaction's sender
--------------------------------------

The results will contain all logs, where the sender of the transaction that caused the log to be emitted
has the specified address.

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/log/_search

JSON body:

.. literalinclude:: log/by_causing_tx_sender.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/log/by_causing_tx_sender.json | http POST https://public.eth.events/ethereum/log/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/log/by_causing_tx_sender.json



Filter by emitting contract
---------------------------

The results will contain all logs that were emitted from the specified contract.

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/log/_search

JSON body:

.. literalinclude:: log/by_emitting_contract.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/log/by_emitting_contract.json | http POST https://public.eth.events/ethereum/log/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/log/by_emitting_contract.json 


Filter by topic[0] signature
----------------------------

The results will contain all logs, that have the specified topic signature
as firs element in their `topics` array.

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/log/_search

JSON body:

.. literalinclude:: log/by_topic_signature.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/log/by_topic_signature.json | http POST https://public.eth.events/ethereum/log/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/log/by_topic_signature.json


Filter by causing transaction's hash
------------------------------------

The results will contain all logs, where the transaction that caused the log to be emitted
has the specified transaction `hash`.


HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/log/_search

JSON body:

.. literalinclude:: log/by_txhash.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/log/by_txhash.json | http POST https://public.eth.events/ethereum/log/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/log/by_txhash.json


Event
~~~~~

Filter by event name
--------------------
The results will contain all events with the specified event name.

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/event/_search

JSON body:

.. literalinclude:: event/by_event_name.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/event/by_event_name.json | http POST https://public.eth.events/ethereum/event/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/event/by_event_name.json


Filter by emitting contract
---------------------------

The results will contain all events that where emitted by the specified contract.

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/event/_search

JSON body:

.. literalinclude:: event/by_contract_address.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/event/by_event_name.json | http POST https://public.eth.events/ethereum/event/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/event/by_event_name.json


Filter by ERC20 contract's address and `from` address
-----------------------------------------------------

The results will contain all events that where emitted by the specified contract, and where the 
`from` argument of the event matches the specifid address. Although this query is tailored for ERC20 contracts, 
there is no parameter that specifically filters for the ERC20 interface.

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/event/_search

JSON body:

.. literalinclude:: event/by_erc20_contract_and_from_address.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/event/by_event_name.json | http POST https://public.eth.events/ethereum/event/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/event/by_event_name.json


Specialised queries
~~~~~~~~~~~~~~~~~~~

Find entity by hash
-------------------

The results will contain either a block with the specified block hash or all transactions, whose sender (`from`) or receiver (`to`) is 
has the specified address.
Queries like this are useful if the type of the entity that a hash represents is not known in advance.

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/block,tx/_search

JSON body:

.. literalinclude:: find_entity_by_hash.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/find_entity_by_hash.json | http POST https://public.eth.events/ethereum/event/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/find_entity_by_hash.json



Get 10 tx and latest block in one query
---------------------------------------

The results will contain 10 transactions in no particular order. Additionally, the results will contain the 
latest block. 

HTTP-Method/Endpoint:

.. code:: bash

      POST /ethereum/block/_search

JSON body:

.. literalinclude:: get_tx_and_latest_block.json

Execute the request with:

``HTTPie``:

.. code:: bash

  http GET https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/get_tx_and_latest_block.json | http POST https://public.eth.events/ethereum/block/_search -a demouser:demouser

To save the JSON body to disk in the UNIX terminal, type:

.. code:: bash

  curl -O https://raw.githubusercontent.com/brainbot-com/ethevents/master/docs/example-queries/get_tx_and_latest_block.json


