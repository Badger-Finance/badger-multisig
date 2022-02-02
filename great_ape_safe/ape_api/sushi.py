from brownie import web3
from great_ape_safe.ape_api.uni_v2 import UniV2
from helpers.addresses import registry


class Sushi(UniV2):
    def __init__(self, safe):
        self.safe = safe

        self.router = safe.contract(registry.eth.sushiswap.routerV2)
        self.factory = safe.contract(registry.eth.sushiswap.factoryV2)

        self.max_slippage = 0.02
        self.max_weth_unwrap = 0.01
        self.deadline = 60 * 60 * 12