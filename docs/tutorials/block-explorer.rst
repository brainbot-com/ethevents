Build a simple blockchain explorer using eth.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: /img/block-explorer.png
    :scale: 50

Introduction
------------

In this tutorial we will build a single page application Ethereum
blockchain explorer that queries it's blockchain data from an eth.events
endpoint.

We assume, that you know how to write ‘eth.events’ ElasticSearch
queries. For more information on how to construct ``eth.events``
elasticsearch queries, have a look
`here <TODO%20crosslink%20to%20query%20tutorial>`__.

We keep it fairly simple by using plain JavaScript (*JS*), jQuery and
the ``json2html`` templating library.

You can find the finished application code `here <TODO>`__.

Our application consists of only two files:

-  ``index.html`` - main application with inline JS code
-  ``queries.js`` - JS functions that return parts of the queries for
   convenience

Basic HTML structure
--------------------

In the ``index.html`` we will first set up the ``<head>``, where some
meta information for the webpage is given and all of the later needed JS
files are imported.

For simplicity, we load every external JS file from Content Delivery
Networks (*CDNs*), so that we don't have to distribute them ourselves.

.. code-block:: html


    <head>
        <meta charset="utf-8">
        <meta name="description" content="eth.events Block Explorer">
        <title>eth.events Block Explorer</title>
        
        <script src="//code.jquery.com/jquery-latest.js"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/json2html/1.2.0/json2html.min.js"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/jquery.json2html/1.2.0/jquery.json2html.min.js"></script>
        <script src="queries.js"></script>
    </head> 

In the example code, there is some additional ``<style>`` information,
in order to have a minimal viable styling in order.

The visible body of our application consists of some input fields and
two tables, that will later on show the results of the ``eth.events``
queries.

The ``<script></script>`` tags on the bottom will contain the JS logic
later on.

User input
----------

.. code-block:: html

    <input id="connection" value="http://localhost:5478"></input>

We will include a ``connection`` input field. This helps us to set the
endpoint of the ``eth.events`` server easily. It defaults to the
eth.events default local endpoint, but you could use a deployed online
version as well.

.. code-block:: html

    <input id="usb" value=""></input><input type="button" value="Search" onClick="search()"></input>

This is the heart of the search engine from the user perspective. The
value entered in the input field will get set to the ``usb`` variable in
JS. A click on the associated button will trigger the ``search()``
function.

Display search results
----------------------

The search result consists of two tables, that will eventually get
filled by JS functions, if a matching result is sent back from the
eth.events server.

.. code-block:: html


    <div id="result">
        <table class="tx"><thead><tr>
                    <td>FROM</td>
                    <td>TO</td>
                    <td>VALUE</td>
                    <td>GAS USED</td>
                    <td>GAS PRICE</td>
                    <td>TX HASH</td>
                    <td>BLOCK #</td>
        </tr></thead><tbody></tbody></table>
        
        <table class="block"><thead><tr>
                    <td>NUMBER</td>
                    <td># TXs</td>
                    <td>TIME</td>
                    <td>HASH</td>
        </tr></thead><tbody></tbody></table>
    </div>

For simplicity, we only allow search results of type "Transaction" and
"Block", and each table carries information, only if the fetched search
results are of its respective type.

Call flow for one search cycle
------------------------------

Let's break down one search cycle from search initiation to displaying
the result:

The text entered into the input-form will set the ``usb`` variable and a
button press on 'Search' will initiate the ``search()`` function:

.. code-block:: javascript

    function search() {
        term = $('#usb').val();
        query = by_hash(term);
        execute_search(query);
    };

The ``term`` variable is retrieved from the input-forms ``#usb`` with
jQuery, similarly to JS' native ``getElementById``.

Construct the queries HTTP body
-------------------------------

The query information to be sent to the ``eth.events`` server is
constructed with the ``by_hash()`` function, implemented in the
``queries.js`` file:

.. code-block:: js

    function by_hash(_hash) {
        // query for finding entities (tx, log) by _hash (id or to/from address)
        return {
            query: {bool: {should: [
                {ids: {values: [_hash]}},
                {term: {from: _hash}},
                {term: {to: _hash}},
            ]}},
            sort: {
                timestamp: "desc"
            }
        }
    }

Making the HTTP request
-----------------------

``execute_search()`` will send the query to the ``eth.events`` server
and handle the results asynchronously:

.. code-block:: js

    function execute_search(query) {
        connection = $('#connection').val();
        $.ajax({
            type: 'POST',
            url: connection + '/ethereum/tx,block/_search',
            data: JSON.stringify(query),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function(response) {
                paste(response);
                
            }
        });
    };

We obtain the ``connection`` variable from the input form. This is the
base-url of the ``eth.events`` server endpoint. The http-request to the
``eth.events`` server will be ``POST``\ ed asynchronously n with
jQuery's `$.ajax() <http://api.jquery.com/jquery.ajax/>`__ method.

The suffix for the server endpoint of the query is
``'/ethereum/tx,block/_search'``. This is because we are searching
either for a transaction on the ``tx``-index or a block on the
``block``-index. If we would only allow block searches, the endpoint
could be reduced to ``'/ethereum/block/_search'`` for efficiency
reasons.

Since we don't use a synchronous request, we have to tell the AJAX
method what to do once a result was returned from the server. This can
be done by providing a callback function to the ``success`` argument.

Receiving server results
------------------------

Once the result is received, the ``paste()`` callback-function will get
called with the servers response.

.. code-block:: js

    function paste(result) {
        txs = result.hits.hits.filter(hit => hit._type == 'tx');
        $('#result table.tx tbody').html('');
        $('#result table.tx tbody').json2html(txs, txtransform);
        
        blocks = result.hits.hits.filter(hit => hit._type == 'block');
        $('#result table.block tbody').html('');
        $('#result table.block tbody').json2html(blocks, blocktransform);
    }

To get more information on how the result is structured, please refer to
the
`documentation <https://github.com/brainbot-com/ethevents/tree/master/docs>`__

Populating the HTML tables
--------------------------

The results will get filtered based on the result type. If the query
returns matching transactions, the ``txs`` list will get populated with
those results. Afterwards it will be passed to our templating engine,
``json2html``, that acts on the ``table.tx``'s ``<tbody>`` element
defined at the beginning.

The actual template is passed as the ``txtransform`` variable. It
contains the skeleton of the transaction tables rows:

.. code-block:: js

    var txtransform = {'<>': 'tr', 'html': [
        {'<>': 'td', 'html': [
            {'<>': 'a', 'href': "javascript:searchterm('${_source.from}')",
                'text': '${_source.from}'}
        ]},
        {'<>': 'td', 'html': [
            {'<>': 'a', 'href': "javascript:searchterm('${_source.to}')",
                'text': '${_source.to}'}
        ]},
        {'<>': 'td', 'html': '${_source.value.eth}'},
        {'<>': 'td', 'html': '${_source.gasUsed.num}'},
        {'<>': 'td', 'html': '${_source.gasPrice.num}'},
        {'<>': 'td', 'class': 'truncate', 'html': '${_source.hash}'},
        {'<>': 'td', 'html': '${_source.blockNumber.num}'},
                ]};

For the specifics of the ``json2html`` templating syntax, please refer
to the `documentation <http://json2html.com/docs/>`__. Here the string
literals will get parsed.The text inside the curly bracket notation will
be interpreted as parameters. It will get substituted with the
parameter's value later on.

For example ``{'<>': 'td', 'html': '${_source.value.eth}'}`` will get
rendered as ``<td>0.24</td>``, when the queried transaction has an
eth-value of ``0.24``.

Cross references and blockchain browsing
----------------------------------------

To allow simple browsing of e.g. the transactions originating account
address, references can also trigger other functions.

.. code-block:: js

    {'<>': 'a', 'href': "javascript:searchterm('${_source.from}')",
     'text': '${_source.from}'}

If the user clicks on the transactions originating address, the
``searchterm()`` function gets executed with the transactions ``from``
address as argument. ``searchterm()`` is similar to the initial
``search()`` function and uses the same ``eth.events`` query.

From here, the search cycle starts again, with a different entity to be
searched. Since the ``_source.from`` argument is an address and not a
transaction hash, the query result will differ:

.. TODO too complicated, change wording

eventually it doesn't return a singular transaction, but multiple hits
of transactions, in which the queried address is involved in.

For the second table, displaying block information, the templating is
very similar to the transaction table: 


.. code-block:: js

    var blocktransform = {'<>': 'tr', 'html': [
        {'<>': 'td', 'html': '${_source.number.num}'},
        {'<>': 'td', 'html': [
            { '<>': 'a', 'href': "javascript:get_tx_for_block('${_source.hash}')",
            'text': '${_source.transactions.length}'},
        ]},
        {'<>': 'td', 'html': '${_source.timestamp}'},
        {'<>': 'td', 'class': 'truncate', 'html': '${_source.hash}'},
        
    ]};

The ``get_tx_for_block()`` function carries out another query with the
blocks hash and retrieves all transactions that are included in the
queried block.

.. code-block:: js

    function get_tx_for_block(blockhash) {
        query = {query: {bool: {filter: [
            {type: {value: 'tx'}},
            {term: {blockHash: blockhash}}
        ]}}}
        execute_search(query);
    };

This get's rendered to the ``table.tx`` as multiple rows of
transactions.

Now, you have seen how simple it is to create a block explorer with
..  TODO how many lines of code?
eth.events and xxx lines of code. You can find the finished application
code
`here <https://github.com/brainbot-com/ethevents/tree/master/docs/example-apps/simple-block-explorer>`__.
