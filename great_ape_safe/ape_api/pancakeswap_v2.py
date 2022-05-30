from great_ape_safe.ape_api.uni_v2 import UniV2
from helpers.addresses import registry


class PancakeswapV2(UniV2):
    def __init__(self, safe):
        self.safe = safe
        self.router = self.safe.contract(registry.bsc.pancakeswap.router_v2)
        self.factory = self.safe.contract(registry.bsc.pancakeswap.factory_v2)
