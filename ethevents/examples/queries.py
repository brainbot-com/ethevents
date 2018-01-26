import units
from ethereum.utils import denoms


def gas_prices_query(
    time_range=dict(gt='now/h-1h'),
    interval=units.si.PREFIXES['G'] * denoms.wei,
):
    """This query aggregates the gas prices two-fold:
        - `gasprice_stats` generates `extended_stats`
        - `gas_price_histogram` counts the number of included transactions in steps of
        `interval` wei.

    Usage:
        es.search('ethereum', 'tx', body=gas_prices_query())

    Params:
        time_range (dict): a range query dictionary for the `timestamp` field
        interval (int): the gas price steps in wei for aggregating transaction numbers
    Returns:
        query (dict): an elasticsearch query body dictionary.
    """
    return dict(
        query={
            'bool': {
                'filter': {
                    'range': {
                        'timestamp': time_range
                    }
                }
            }
        },
        size=0,
        aggs=dict(
            gasprice_stats=dict(
                extended_stats=dict(
                    field='gasPrice.num'
                )
            ),
            gas_price_histogram=dict(
                histogram=dict(
                    field='gasPrice.num',
                    interval=interval,
                    min_doc_count=1
                )
            )
        )
    )


def common_event_topics(num_topics=10, num_contracts=10, only_sigs=False):
    """This query aggregates the most common event signatures and their most common contract
    addresses.

    Usage:
        es.search('ethereum', 'log', body=common_event_topics())

    Params:
        num_topics (int): maximum number of topics to collect
        num_contracts (int): maximum number of contract addresses per topic
        only_sigs (bool): if true, only collect `topic0`
    Returns:
        query (dict): an elasticsearch query body dictionary.
    """
    return {
        "query": {
            "match_all": {}
        },
        "aggs": {
            "topic": {
                "terms": {
                    "field": "signature" if only_sigs else "topics",
                    "size": num_topics
                },
                "aggs": {
                    "contract": {
                        "terms": {
                            "field": "address",
                            "size": num_contracts
                        }
                    }
                }
            }
        },
        "size": 0
    }


def gas_prices_for_event(
    # default ERC20 Transfer(from, to, value)
    event_sig='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
    interval=units.si.PREFIXES['G'] * denoms.wei,
    time_range=dict(gt='now - 7d')
):
    """This query aggregates the gas prices for all transactions that lead to a
    certain `event_sig` topic:
        - `gasprice_stats` generates `extended_stats`
        - `gas_price_histogram` counts the number of included transactions in steps of
        `interval` wei.

    Usage:
        es.search('ethereum', 'tx', body=gas_prices_for_event())

    Params:
        event_sig (str): an event signature (topics[0])
        time_range (dict): a range query dictionary for the `timestamp` field
        interval (int): the gas price steps in wei for aggregating transaction numbers
    Returns:
        query (dict): an elasticsearch query body dictionary.
    """
    return dict(
        query={
            'bool': {
                'filter': dict(
                    has_child=dict(
                        type='log',
                        query=dict(
                            match=dict(
                                signature=event_sig
                            )
                        )
                    )
                )
            }
        },
        aggs=dict(
            gasprice_stats=dict(
                extended_stats=dict(
                    field='gasPrice.num'
                )
            ),
            gas_price_histogram=dict(
                histogram=dict(
                    field='gasPrice.num',
                    interval=interval,
                    min_doc_count=1
                )
            )
        ),
        size=0
    )


def caller_for_event(
    event_sig='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
    time_range=dict(gt=0),
    num_callers=10,
):
    """This query aggregates the most common caller addresses for all transactions
    that lead to a certain `event_sig` topic:
        - `caller` collects the `num_callers` most common sender addresses
        - `gasprice_stats` aggregates gas price statistics per caller

    Usage:
        es.search('ethereum', 'tx', body=caller_for_event())

    Params:
        event_sig (str): an event signature (topics[0])
        time_range (dict): a range query dictionary for the `timestamp` field (default: all time)
        num_callers (int): number of top caller addresses to return
    Returns:
        query (dict): an elasticsearch query body dictionary.
    """
    return dict(
        query={
            'bool': {
                'filter': dict(
                    has_child=dict(
                        type='log',
                        query=dict(
                            match=dict(
                                signature=event_sig
                            )
                        )
                    )
                )
            }
        },
        aggs=dict(
            caller=dict(
                terms=dict(
                    field='from',
                    size=num_callers
                ),
                aggs=dict(
                    gasprice_stats=dict(
                        stats=dict(
                            field='gasPrice.num'
                        )
                    )
                )
            )
        ),
        size=0
    )


def last_transactions_to(
    target_address='0xfb6916095ca1df60bb79ce92ce3ea74c37c5d359',
):
    """Query that returns transactions to `target_address`.
    You can limit the number of responses by tweaking the `size` parameter of `es.search(...)`.

    Usage:
        es.search('ethereum', 'tx', body=last_transactions_to(), size=5)

    Params:
        target_address (str): the transaction target address (`to`)
    Returns:
        query (dict): elasticsearch query body dictionary.
    """
    return dict(
        query=dict(
            match=dict(
                to=target_address
            )
        ),
        sort={
            'blockNumber.num': 'desc'
        }
    )


def last_blocks_with_address(
    address='0xfb6916095ca1df60bb79ce92ce3ea74c37c5d359'
):
    """Query that returns blocks, that had transactions to or from `address`.
    You can limit the number of responses by tweaking the `size` parameter of `es.search(...)`.

    Usage:
        es.search('ethereum', 'block', body=last_blocks_with_address(), size=1)

    Params:
        address (str): the address that should have been touched in the block's
                        transactions (`to`/`from`)
    Returns:
        query (dict): elasticsearch query body dictionary.
    """
    return dict(
        query={
            'bool': {
                'filter': dict(
                    has_child=dict(
                        type='tx',
                        query=dict(
                            multi_match=dict(
                                query=address,
                                fields=['to', 'from']
                            )
                        )
                    )
                )
            }
        },
        sort={
            'number.num': 'desc'
        }
    )


def last_blocks_that_logged(
    event_sig='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
):
    """Query that returns blocks, that had `event_sig` log events.
    You can limit the number of responses by tweaking the `size` parameter of `es.search(...)`.

    Usage:
        es.search('ethereum', 'block', body=last_blocks_that_logged(), size=5)

    Params:
        event_sig (str): an event signature (topics[0])
    Returns:
        query (dict): elasticsearch query body dictionary.
    """
    return dict(
        query={
            'bool': {
                'filter': dict(
                    has_child=dict(
                        type='tx',
                        query=dict(
                            has_child=dict(
                                type='log',
                                query=dict(
                                    match=dict(
                                        signature=event_sig
                                    )
                                )
                            )
                        )
                    )
                )
            }
        },
        sort={
            'number.num': 'desc'
        }
    )
