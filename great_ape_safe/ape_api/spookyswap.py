from great_ape_safe.ape_api.uni_v2 import UniV2
from helpers.addresses import registry


class Spookyswap(UniV2):
    def __init__(self, safe):
        self.safe = safe
        self.router = self.safe.contract(registry.ftm.spookyswap.router)
        self.factory = self.safe.contract(registry.ftm.spookyswap.factory)

    max_slippage = 0.05
