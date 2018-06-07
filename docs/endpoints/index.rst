Index endpoints
======================================

Eth.events currently has 4 endpoints for the different entities on the Ethereum blockchain:

- `block` 
- `tx`
- `log`
- `event`

Searches on the eth.events index can address a specific endpoint, so that the endpoint itself
already functions as a filter for the specified entity.


- For example, a search request to `/ethereum/event/` will only show `event` typed objects.

.. TODO provide copy+pasteable command


Endpoints also can be combined, to widen the scope of the query:

- A search request to `/ethereum/event,tx/` will only show `event` and `tx` typed objects.

.. TODO provide copy+pasteable command

The following chapters will document the available entities and explain it's property structure.

.. toctree::
   :maxdepth: 2

   block
   tx
   log
   event
