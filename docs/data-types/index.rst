Data types
==========

Elasticsearch types
~~~~~~~~~~~~~~~~~~~

All the types from the blockchain as well as their encodings have to be represented with a Elasticsearch type
for indexing and searching. Most blockchain types that are no number types are represented as a string in Elasticsearch (`keyword` or `text` type).

To learn more about the types in Elasticsearch, visit their `documentation <https://www.elastic.co/guide/en/elasticsearch/reference/5.6/mapping-types.html>`__.



Eth.events encoded types
~~~~~~~~~~~~~~~~~~~~~~~~~

This are the types that represent a value on the blockchain. For some values, there are alternative encodings available.

raw
"""
The raw value as read by the ethereum node used for indexing. This corresponds to the normal type as defined in 
the `web3 API`.
Implemented as a `keyword` type in Elasticsearch.

eth
"""
A double floating point number that directly represents the ether value. Due to rounding this 
is not as accurate as using the `raw` value directly.
Implemented as a `double` type in Elasticsearch.

padded
""""""
A hexadecimal data type, where the hex string is padded to the biggest possible value.
This allows for easier string sorting of values.
Implemented as a `keyword` type in Elasticsearch.

num
"""
An integer representation of a value.
Implemented as a `long` type in Elasticsearch.

hex
"""
A hex string, representing raw hex values exclusively. 
Implemented as a `keyword` type in Elasticsearch.

keyword
"""""""
An explicit property that makes the `keyword` Elasticsearch type of a string accessible,
when the default value is of type `text`. This is useful for allowing literal searches instead of
pattern matching text searches.
Implemented as a `keyword` type in Elasticsearch.




