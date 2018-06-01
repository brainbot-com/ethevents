Transaction
===========

.. TODO brief explanation of a block, what is special in eth events etc



Object description
~~~~~~~~~~~~~~~~~~

The `tx` object inherits it's properties from the transaction object, as specified in the `web3 API <https://github.com/ethereum/wiki/wiki/JavaScript-API#web3ethgettransaction>`__:


  - `from`: `String` - The address for the sending account. Uses the web3.eth.defaultAccount property, if not specified.
  - `to`: `String` - (optional) The destination address of the message, left undefined for a contract-creation transaction.
  - `value`: `Number|String|BigNumber` - (optional) The value transferred for the transaction in Wei, also the endowment if it's a contract-creation transaction.
  - `gas`: `Number|String|BigNumber` - (optional, default: To-Be-Determined) The amount of gas to use for the transaction (unused gas is refunded).
  - `gasPrice`: `Number|String|BigNumber` - (optional, default: To-Be-Determined) The price of gas for this transaction in wei, defaults to the mean network gas price.
  - `data`: `String` - (optional) Either a byte string containing the associated data of the message, or in the case of a contract-creation transaction, the initialisation code.
  - `nonce`: `Number`  - (optional) Integer of a nonce. This allows to overwrite your own pending transactions that use the same nonce.

.. TODO add additional and remove missing fields from eth.events, but make visible the diff to the web3 docs
.. TODO clean up the descriptions from unneccesary web3 annotations

Mapping
~~~~~~~

All fields with types `String` in the official web3 specification are indexed with a `keyword` type, which allows exact matching on the field.
For `Number` typed fields, we provide alternative encodings to the `raw` hex-value, to allow for a streamlined, human readable representation.

.. TODO explain num, raw, padded for Number types



.. literalinclude:: ../mappings/tx.json
	:language: json
