# coding: utf-8
"""
The event spec can be found here:
    https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI#events
"""
from web3.utils import events


class EventABI(object):
    """This class contains some class methods to simplify working with event abis."""

    @classmethod
    def only_events(abilist):
        """Filter a contract ABI to return only 'event' entries"""
        return list(filter(lambda a: a['type'] == 'event', abilist))

    @classmethod
    def abi_to_topic0_dict(abi):
        """Map ABI event entries by their `topic0` hex key"""
        result = dict()
        for event_abi in EventABI.only_events(abi):
            result[events.construct_event_topic_set(event_abi)[0][0]] = event_abi
        return result

    @classmethod
    def abi_to_format_string(event_abi):
        """Create a python format string for transforming a translated event into
        human readable form.

        To translate events, use

            from web3.utils import events
            events.get_event_data(event_abi, event_doc)

        where `event_abi` is a single events abi dictionary and `event_doc` is the
        `_source` portion of a `/ethereum/log` document from the eth.events Elasticsearch
        index.
        """
        params = ['{%s}' % param['name'] for param in event_abi['inputs']]
        return '{}({})'.format(
            event_abi['name'],
            ', '.join(
                str(param) for param in params
            )
        )
