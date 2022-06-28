from brownie import ZERO_ADDRESS, interface

from helpers.addresses import r


class Maker:
    def __init__(self, safe):
        self.safe = safe

        # contracts
        self.proxy_registry = self.safe.contract(
            r.maker.proxy_registry, interface.IProxyRegistry
        )
        if self.proxy_registry.proxies(safe) == ZERO_ADDRESS:
            self.proxy = None
        else:
            self.proxy = self.safe.contract(
                self.proxy_registry.proxies(safe), interface.IDSProxy
            )


    def build_proxy(self):
        self.proxy_registry.build()
        # reinit so self.proxy can be properly set
        self.__init__(self.safe)
