from brownie import interface

from great_ape_safe.ape_api.curve import Curve
from helpers.addresses import registry


class CurveV2(Curve):
    def __init__(self, safe):
        self.safe = safe
        # tokens
        self.crv = interface.ERC20(registry.eth.treasury_tokens.CRV)
        # contracts
        self.provider = safe.contract(registry.eth.curve.provider)
        # self.registry = safe.contract(self.provider.get_registry())
        self.registry   = safe.contract(registry.eth.curve.factory)
        self.exchanger = safe.contract(self.provider.get_address(2))
        self.metapool_registry = safe.contract(self.provider.get_address(3))
        self.crypto_registry = safe.contract(self.provider.get_address(5))
        # parameters
        self.max_slippage_and_fees = .02
        self.is_v2 = True
