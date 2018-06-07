Event
=====

Object schema
~~~~~~~~~~~~~~~~~~

- `address`: `String`- address from which this event originated.
- `args`: `Array` - Array of argument objects coming from that event.
- `blockHash`: `String` - hash of the block where this event was in.
- `blockNumber`: `Number` - the block number where this event was in.
- `logIndex`: `Number` - integer of the event index position in the block.
- `event`: `String` - The event name.
- `transactionIndex`: `Number` - integer of the transactions index position event was created from.
- `transactionHash`: `String`- hash of the transactions this event was created from.


Event arguments
~~~~~~~~~~~~~~~

The event's arguments with it's corresponding values are located in an object representation in an array of arguments.
This allows different events to have different types and numbers of arguments.

The argument object's structure:

- `name` - the argument's name in human readable form
- `pos` -  the index of the argument's position in the event
- `value.hex`,`value.scaled`, `value.num` - the value of the events argument in it's corresponding representation
- `value.type` - the type of the argument's value, can be any type as specified for Solidity 


Mapping
~~~~~~~

For some fields, there are multiple encodings available, which are nested as properties on the field.
More information on those data types can be found :doc:`here </data-types/index>`.

The following is the output of the Elasticsearch mapping for the `Event` type:



.. literalinclude:: ../mappings/event.json
	:language: json
