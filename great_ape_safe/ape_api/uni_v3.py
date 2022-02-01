import json
import os
from brownie import interface, Contract
from helpers.addresses import registry


class UniV3:
    def __init__(self, safe):
        self.safe = safe

        # contracts
        self.nonfungible_position_manager = interface.INonFungiblePositionManager(
            registry.eth.uniswap.NonfungiblePositionManager, owner=self.safe.account
        )
        self.v3pool_wbtc_badger = interface.IUniswapV3Pool(
            registry.eth.uniswap.v3pool_wbtc_badger, owner=self.safe.account
        )

        # constant helpers
        self.Q128 = 2 ** 128

    def collect_fees(self):
        """
        loop over `TCL/positionData/` directory to grab each tokenID
        to allow us to claim the fees earned on each range over time
        """
        path = os.path.dirname(f"scripts/TCL/positionData/")
        directory = os.fsencode(path)

        token0 = Contract(self.v3pool_wbtc_badger.token0())
        token1 = Contract(self.v3pool_wbtc_badger.token1())

        token0_bal_init = token0.balanceOf(self.safe.address)
        token1_bal_init = token1.balanceOf(self.safe.address)

        for file in os.listdir(directory):
            filename = os.fsdecode(file)

            with open(f"scripts/TCL/positionData/{filename}") as f:
                json_info = json.load(f)
                token_id = json_info["tokenId"]

                # https://docs.uniswap.org/protocol/reference/periphery/interfaces/INonfungiblePositionManager#collectparams
                params = (token_id, self.safe.address, self.Q128 - 1, self.Q128 - 1)

                self.nonfungible_position_manager.collect(params)

        # check that increase the balance off-chain
        assert token0.balanceOf(self.safe.address) > token0_bal_init
        assert token1.balanceOf(self.safe.address) > token1_bal_init
