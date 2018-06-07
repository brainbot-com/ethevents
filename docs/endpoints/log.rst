Log
===

Object schema
~~~~~~~~~~~~~

The `log` object inherits it's properties from the `web3 API <https://github.com/ethereum/wiki/wiki/JavaScript-API#web3ethfilter>`__:


- `logIndex`: `Number` - integer of the log index position in the block.
- `transactionIndex`: `Number` - integer of the transactions index position log was created from. 
- `transactionHash`: `String`- hash of the transactions this log was created from.
- `blockHash`: `String` - hash of the block where this log was in. `null` when its pending.
- `blockNumber`: `Number` - the block number where this log was in. `null` when its pending.
- `address`: `String` - address from which this log originated.
- `data`: `String` - contains one or more non-indexed arguments of the log.
- `topics`: `Array of hex strings` - Array of indexed log arguments.


Mapping
~~~~~~~

For some fields, there are multiple encodings available, which are nested as properties on the field.
More information on those data types can be found :doc:`here </data-types/index>`.

The following is the output of the Elasticsearch mapping for the `Log` type:


.. literalinclude:: ../mappings/log.json
	:language: json
