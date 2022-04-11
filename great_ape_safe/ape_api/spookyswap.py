from great_ape_safe.ape_api.uni_v2 import UniV2
from helpers.addresses import registry


class SpookySwap(UniV2):
    def __init__(self, safe):
        super().__init__(safe)

        self.router = safe.contract(registry.ftm.spookyswap.router)
        self.factory = safe.contract(registry.ftm.spookyswap.factory)

        self.max_slippage = 0.05
