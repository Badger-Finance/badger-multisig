from great_ape_safe.ape_api.uni_v2 import UniV2
from helpers.addresses import registry


class PancakeswapV2(UniV2):
    def __init__(self, safe):
        super().__init__(safe)

        self.router = safe.contract(registry.bsc.pancakeswap.router_v2)
        self.factory = safe.contract(registry.bsc.pancakeswap.factory_v2)
