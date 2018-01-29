from typing import Union

from eth_utils import encode_hex

from ethevents.client.app import App
from ethevents.types import Address


class AccountUI(object):
    def __init__(self, app: App):
        self.app = app

    def channel_balance(self) -> Union[int, None]:
        """
        Check the RDN balance in Rei of the channel currently used for µRaiden requests. If no
        request has been made yet, no channel will be set and None is returned.
        """
        if self.app.session.channel is None:
            print('No channel opened yet.')
            return None
        return self.app.session.channel.balance

    def ether_balance(self) -> int:
        """
        Check the ETH balance in Wei of the current account.
        """
        self.app.account.sync_balances()
        return self.app.account.wei_balance

    def rdn_balance(self) -> int:
        """
        Check the RDN balance in Rei of the current account.
        """
        self.app.account.sync_balances()
        return self.app.account.rei_balance

    def close_channel(self):
        """
        Closes the µRaiden channel to the server by requesting a closing signature from the server.
        If not closing signature is returned, the channel is closed non-cooperatively.
        """
        self.app.session.close_channel()

    def drain(self, to: Address, rdn: bool = False, rdn_and_eth: bool = False):
        """
        Drains RDN tokens or ETH from the eth.events account to a target address.

        :param to: The sink address to send the ETH or tokens to. This address must be in a
                   checksummed format.
        :param rdn: True if all RDN tokens should be drained from the eth.events account.
        :param rdn_and_eth: True if both all RDN tokens and all ETH should be drained from the
                            eth.events account.
        """
        self.app.drain(to, rdn=rdn, rdn_and_eth=rdn_and_eth)

    def address(self) -> Address:
        """
        Returns the address of the eth.events account used for µRaiden payment channels.
        """
        return self.app.account.address

    def channel_key(self) -> Union[str, None]:
        """
        Returns the channel key of the currently active channel used for µRaiden requests.
        """
        if self.app.session.channel is None:
            return None
        return encode_hex(self.app.session.channel.key)
