Block
=====

.. TODO brief explanation of a block, what is special in eth events etc



Object description
~~~~~~~~~~~~~~~~~~
The block object inherits it's properties from the `web3 API <https://github.com/ethereum/wiki/wiki/JavaScript-API#web3ethgetblock>`__:


  - `number`: `Number` - the block number. `null` when its pending block.
  - `hash`: `String`, 32 Bytes - hash of the block. `null` when its pending block.
  - `parentHash`: `String`, 32 Bytes - hash of the parent block.
  - `nonce`: `String`, 8 Bytes - hash of the generated proof-of-work. `null` when its pending block.
  - `sha3Uncles`: `String`, 32 Bytes - SHA3 of the uncles data in the block.
  - `logsBloom`: `String`, 256 Bytes - the bloom filter for the logs of the block. `null` when its pending block.
  - `transactionsRoot`: `String`, 32 Bytes - the root of the transaction trie of the block
  - `stateRoot`: `String`, 32 Bytes - the root of the final state trie of the block.
  - `miner`: `String`, 20 Bytes - the address of the beneficiary to whom the mining rewards were given.
  - `difficulty`: `BigNumber` - integer of the difficulty for this block.
  - `totalDifficulty`: `BigNumber` - integer of the total difficulty of the chain until this block.
  - `extraData`: `String` - the "extra data" field of this block.
  - `size`: `Number` - integer the size of this block in bytes.
  - `gasLimit`: `Number` - the maximum gas allowed in this block.
  - `gasUsed`: `Number` - the total used gas by all transactions in this block.
  - `timestamp`: `Number` - the unix timestamp for when the block was collated.
  - `transactions`: `Array` - Array of transaction objects, or 32 Bytes transaction hashes depending on the last given parameter.
  - `uncles`: `Array` - Array of uncle hashes.

.. TODO add additional and remove missing fields from eth.events, but make visible the diff to the web3 docs

Mapping
~~~~~~~

All fields with types `String` in the official web3 specification are indexed with a `keyword` type, which allows exact matching on the field.
For `Number` typed fields, we provide alternative encodings to the `raw` hex-value, to allow for a streamlined, human readable representation.

.. TODO explain num, raw, padded for Number types



.. literalinclude:: ../mappings/block.json
	:language: json
