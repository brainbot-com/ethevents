Block
=====

Object schema
~~~~~~~~~~~~~
The block object inherits it's properties from the `web3 API <https://github.com/ethereum/wiki/wiki/JavaScript-API#web3ethgetblock>`__:


  - `number`: `Number` - the block number.
  - `hash`: `String` - hash of the block.
  - `parentHash`: `String` - hash of the parent block.
  - `nonce`: `String` - hash of the generated proof-of-work.
  - `sha3Uncles`: `String` - SHA3 of the uncles data in the block.
  - `logsBloom`: `String` - the bloom filter for the logs of the block.
  - `transactionsRoot`: `String`- the root of the transaction trie of the block
  - `stateRoot`: `String` - the root of the final state trie of the block.
  - `miner`: `String` - the address of the beneficiary to whom the mining rewards were given.
  - `difficulty`: `BigNumber` - integer of the difficulty for this block.
  - `totalDifficulty`: `BigNumber` - integer of the total difficulty of the chain until this block.
  - `extraData`: `String` - the "extra data" field of this block.
  - `size`: `Number` - integer the size of this block in bytes.
  - `gasLimit`: `Number` - the maximum gas allowed in this block.
  - `gasUsed`: `Number` - the total used gas by all transactions in this block.
  - `timestamp`: `Number` - the unix timestamp for when the block was collated.
  - `transactions`: `Array` - Array of transaction hashes
  - `uncles`: `Array` - Array of uncle hashes.


Mapping
~~~~~~~

For some fields, there are multiple encodings available, which are nested as properties on the field.
More information on those data types can be found :doc:`here </data-types/index>`.

The following is the output of the Elasticsearch mapping for the `Block` type:


.. literalinclude:: /mappings/block.json
	:language: json
