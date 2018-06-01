Event
=====

.. TODO brief explanation of an Event, what is special in eth events etc

.. TODO explain that there is no event object in the web3 specs,
.. and that we generate it from the ABI etc

Object description
~~~~~~~~~~~~~~~~~~


.. TODO explain fields of event


Mapping
~~~~~~~

All fields with types `String` in the official web3 specification are indexed with a `keyword` type, which allows exact matching on the field.
For `Number` typed fields, we provide alternative encodings to the `raw` hex-value, to allow for a streamlined, human readable representation.

.. TODO explain num, raw, padded for Number types



.. literalinclude:: ../mappings/event.json
	:language: json
