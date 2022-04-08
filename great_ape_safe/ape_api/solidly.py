from great_ape_safe.ape_api.uni_v2 import UniV2
from helpers.addresses import registry


class Solidly(UniV2):
    def __init__(self, safe):
        self.safe = safe

        self.router = safe.contract(registry.ftm.solidly.router)
        self.factory = safe.contract(self.router.factory())

        self.max_slippage = 0.05
        self.max_weth_unwrap = 0.01
        self.deadline = 60 * 60 * 12
        self.native_symbol = 'FTM'
