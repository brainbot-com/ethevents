Log
===

.. TODO brief explanation of a block, what is special in eth events etc



Object description
~~~~~~~~~~~~~~~~~~

The `log` object inherits it's properties from the `web3 API <https://github.com/ethereum/wiki/wiki/JavaScript-API#web3ethfilter>`__:


- `logIndex`: `Number` - integer of the log index position in the block. `null` when its pending log.
- `transactionIndex`: `Number` - integer of the transactions index position log was created from. `null` when its pending log.
- `transactionHash`: `String`, 32 Bytes - hash of the transactions this log was created from. `null` when its pending log.
- `blockHash`: `String`, 32 Bytes - hash of the block where this log was in. `null` when its pending. `null` when its pending log.
- `blockNumber`: `Number` - the block number where this log was in. `null` when its pending. `null` when its pending log.
- `address`: `String`, 32 Bytes - address from which this log originated.
- `data`: `String` - contains one or more 32 Bytes non-indexed arguments of the log.
- `topics`: `Array of Strings` - Array of 0 to 4 32 Bytes `DATA` of indexed log arguments. (In *solidity*: The first topic is the *hash* of the signature of the event (e.g. `Deposit(address,bytes32,uint256)`), except if you declared the event with the `anonymous` specifier.)
- `type`: `STRING` - `pending` when the log is pending. `mined` if log is already mined.

.. TODO add additional and remove missing fields from eth.events, but make visible the diff to the web3 docs

Mapping
~~~~~~~

All fields with types `String` in the official web3 specification are indexed with a `keyword` type, which allows exact matching on the field.
For `Number` typed fields, we provide alternative encodings to the `raw` hex-value, to allow for a streamlined, human readable representation.

.. TODO explain num, raw, padded for Number types



.. literalinclude:: ../mappings/log.json
	:language: json
