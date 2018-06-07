Transaction
===========

Object schema 
~~~~~~~~~~~~~
The `tx` object inherits it's properties from the transaction object, as specified in the `web3 API <https://github.com/ethereum/wiki/wiki/JavaScript-API#web3ethgettransaction>`__:


  - `from`: `String` - The address for the sending account. Uses the web3.eth.defaultAccount property, if not specified.
  - `to`: `String` - (optional) The destination address of the message, left undefined for a contract-creation transaction.
  - `value`: `Number|String|BigNumber` - (optional) The value transferred for the transaction in Wei, also the endowment if it's a contract-creation transaction.
  - `gas`: `Number|String|BigNumber` - (optional) The amount of gas to use for the transaction (unused gas is refunded).
  - `gasPrice`: `Number|String|BigNumber` - (optional) The price of gas for this transaction in wei, defaults to the mean network gas price.
  - `data`: `String` - (optional) Either a byte string containing the associated data of the message, or in the case of a contract-creation transaction, the initialisation code.
  - `nonce`: `Number` - (optional) Integer of a nonce. This allows to overwrite your own pending transactions that use the same nonce.


Mapping
~~~~~~~

For some fields, there are multiple encodings available, which are nested as properties on the field.
More information on those data types can be found :doc:`here </data-types/index>`.

The following is the output of the Elasticsearch mapping for the `Transaction` type:


.. literalinclude:: ../mappings/tx.json
	:language: json
