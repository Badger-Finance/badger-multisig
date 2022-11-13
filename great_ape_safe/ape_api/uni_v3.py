import json
import os
from datetime import datetime
import math
from pathlib import Path

from brownie import interface, chain, multicall, web3, ZERO_ADDRESS

from helpers.addresses import registry

# general helpers and sdk
from great_ape_safe.ape_api.helpers.uni_v3.uni_v3 import (
    print_position,
    calc_all_accum_fees,
)
from great_ape_safe.ape_api.helpers.uni_v3.uni_v3_sdk import (
    getAmountsForLiquidity,
    getSqrtRatioAtTick,
    getAmount1Delta,
    getAmount0Delta,
    maxLiquidityForAmounts,
    BASE,
)


class UniV3:
    def __init__(self, safe):
        self.safe = safe

        # contracts
        self.nonfungible_position_manager = interface.INonFungiblePositionManager(
            registry.eth.uniswap.NonfungiblePositionManager, owner=self.safe.account
        )
        self.factory = interface.IUniswapV3Factory(
            registry.eth.uniswap.factoryV3, owner=self.safe.account
        )
        self.router = interface.ISwapRouter(
            registry.eth.uniswap.routerV3, owner=self.safe.account
        )
        self.quoter = interface.IQuoter(
            registry.eth.uniswap.quoter, owner=self.safe.account
        )
        self.v3pool_wbtc_badger = interface.IUniswapV3Pool(
            registry.eth.uniswap.v3pool_wbtc_badger, owner=self.safe.account
        )

        # constant helpers
        self.Q128 = 2 ** 128
        self.deadline = 60 * 180
        self.slippage = 0.98

    def _get_pool(self, position):
        return interface.IUniswapV3Pool(
            self.factory.getPool(
                position["token0"], position["token1"], position["fee"]
            ),
            owner=self.safe.account,
        )

    def _build_multihop_path(self, path):
        # given a token path, construct a multihop swap path by adding token pair pools with highest liquidity
        # https://docs.uniswap.org/protocol/guides/swaps/multihop-swaps#input-parameters
        multihop = [path[0].address]
        for i in range(len(path) - 1):
            fee_tiers = {100: 0, 3000: 0, 10000: 0}
            for tier in fee_tiers.keys():
                pool_addr = self.factory.getPool(path[i], path[i + 1], tier)

                if pool_addr == ZERO_ADDRESS:
                    continue

                pool = interface.IUniswapV3Pool(pool_addr)
                fee_tiers[tier] = pool.liquidity()

            if list(fee_tiers.values()).count(0) == 3:
                raise Exception(
                    f"No liquidity found for {path[i].symbol()} - {path[i+1].symbol()}"
                )

            best_tier = max(fee_tiers, key=fee_tiers.get)
            multihop.append(best_tier)
            multihop.append(path[i + 1].address)

        return multihop

    def burn_token_id(self, token_id, burn_nft=False):
        """
        It will decrease the liquidity from a specific NFT
        and collect the fees earned on it
        optional: to completly burn the NFT
        """
        position = self.nonfungible_position_manager.positions(token_id)
        deadline = chain.time() + self.deadline

        pool = self._get_pool(position)

        liquidity = position["liquidity"]
        sqrtRatioX96, _, _, _, _, _, _ = pool.slot0()
        sqrtRatio_lower_tick = getSqrtRatioAtTick(position["tickLower"])
        sqrtRatio_upper_tick = getSqrtRatioAtTick(position["tickUpper"])

        amount0Min, amount1Min = getAmountsForLiquidity(
            sqrtRatioX96, sqrtRatio_lower_tick, sqrtRatio_upper_tick, liquidity
        )

        # requires to remove all liquidity first
        self.nonfungible_position_manager.decreaseLiquidity(
            (
                token_id,
                liquidity,
                amount0Min * self.slippage,
                amount1Min * self.slippage,
                deadline,
            )
        )

        # grab also tokens owned, otherwise cannot burn. ref: https://etherscan.io/address/0xc36442b4a4522e871399cd717abdd847ab11fe88#code#F1#L379
        position = self.nonfungible_position_manager.positions(token_id)

        if position["tokensOwed0"] > 0 or position["tokensOwed1"] > 0:
            print("\nTokens pendant of being collected. Collecting...")

            token0 = self.safe.contract(pool.token0())
            token1 = self.safe.contract(pool.token1())

            token0_bal_init = token0.balanceOf(self.safe.address)
            token1_bal_init = token1.balanceOf(self.safe.address)

            self.collect_fee(token_id)

            # check that increase the balance off-chain
            assert token0.balanceOf(self.safe.address) > token0_bal_init
            assert token1.balanceOf(self.safe.address) > token1_bal_init

        # usually we do not burn the nft, as it is more efficient to leave it empty and fill it up as needed
        if burn_nft:
            # needs to be liq = 0, cleared the pos, otherwise will revert!
            self.nonfungible_position_manager.burn(token_id)

    def collect_fee(self, token_id):
        """
        collect fees for individual token_id
        """
        # docs: https://docs.uniswap.org/protocol/reference/periphery/NonfungiblePositionManager#collect
        # https://docs.uniswap.org/protocol/reference/periphery/interfaces/INonfungiblePositionManager#collectparams
        params = (token_id, self.safe.address, self.Q128 - 1, self.Q128 - 1)

        # revert to this snapshot in case the collected amounts are 0
        # using collect.call somehow always returns 0, even when there are
        # indeed fees to collect
        chain.snapshot()

        # https://etherscan.io/address/0xC36442b4a4522E871399CD717aBDD847Ab11FE88#code#F1#L314
        amount0, amount1 = self.nonfungible_position_manager.collect(
            params
        ).return_value

        if amount0 == 0 and amount1 == 0:
            chain.revert()

    def collect_fees(self):
        """
        loop over all token ids owned by the safe
        to allow us to claim the fees earned on each range over time
        """
        nfts_owned = self.nonfungible_position_manager.balanceOf(self.safe) - 1

        if nfts_owned >= 0:
            with multicall:
                token_ids = [
                    self.nonfungible_position_manager.tokenOfOwnerByIndex(self.safe, i)
                    for i in range(nfts_owned)
                ]

            for token_id in token_ids:
                self.collect_fee(token_id)
        else:
            print(f" === Safe ({self.safe.address}) does not own any NFT === ")

    def increase_liquidity(
        self, token_id, token0, token1, token0_amount_topup, token1_amount_topup
    ):
        """
        Allows to increase liquidity of a specific NFT,
        bare in if it is on an activiy NFT range, proportions will depend
        on where the current tick is
        """
        # docs: https://docs.uniswap.org/protocol/reference/periphery/NonfungiblePositionManager#increaseliquidity
        position = self.nonfungible_position_manager.positions(token_id)

        pool = self._get_pool(position)

        lower_tick = position["tickLower"]
        upper_tick = position["tickUpper"]
        deadline = chain.time() + self.deadline

        # check allowances & approve for topup token amounts if needed
        allowance0 = token0.allowance(
            self.safe.address, self.nonfungible_position_manager
        )
        allowance1 = token1.allowance(
            self.safe.address, self.nonfungible_position_manager
        )

        if allowance0 < token0_amount_topup:
            token0.approve(self.nonfungible_position_manager, token0_amount_topup)
        if allowance1 < token1_amount_topup:
            # badger token does not allow setting !=0 to a new value, 1st set to 0
            if allowance1 > 0 and token1.address == registry.eth.treasury_tokens.BADGER:
                token1.approve(self.nonfungible_position_manager, 0)
            token1.approve(self.nonfungible_position_manager, token1_amount_topup)

        # calcs for min amounts
        # for now leave it just for our wbtc/badger pool "hardcoded" as for sometime doubt we will operate other univ3 pool
        sqrtRatioX96, currentTick, _, _, _, _, _ = pool.slot0()
        sqrtRatio_lower_tick = getSqrtRatioAtTick(lower_tick)
        sqrtRatio_upper_tick = getSqrtRatioAtTick(upper_tick)

        amount0Min = 0
        amount1Min = 0

        liquidity = maxLiquidityForAmounts(
            sqrtRatioX96,
            sqrtRatio_lower_tick,
            sqrtRatio_upper_tick,
            token0_amount_topup,
            token1_amount_topup,
        )

        if currentTick < lower_tick:
            # calc amount0Min
            amount0Min = getAmount0Delta(
                sqrtRatio_lower_tick, sqrtRatio_upper_tick, liquidity
            )
            amount1Min = 0
        elif currentTick < upper_tick:
            # calc both
            amount0Min = getAmount0Delta(sqrtRatioX96, sqrtRatio_upper_tick, liquidity)
            amount1Min = getAmount1Delta(sqrtRatio_lower_tick, sqrtRatioX96, liquidity)
        else:
            # calculate amount1Min
            amount0Min = 0
            amount1Min = getAmount1Delta(
                sqrtRatio_lower_tick, sqrtRatio_upper_tick, liquidity
            )

        # printout before increasing
        print(f"Token ID: {token_id} status position prior to increase liquidity...")
        position_before = print_position(self.nonfungible_position_manager, token_id)
        print(f" ===== Current tick: {currentTick} ===== ")
        print(
            f" ===== amount0Min={amount0Min/10**token0.decimals()}, amount1Min={amount1Min/10**token1.decimals()} ===== \n"
        )

        # https://docs.uniswap.org/protocol/reference/periphery/interfaces/INonfungiblePositionManager#increaseliquidityparams
        params = (
            token_id,
            token0_amount_topup,
            token1_amount_topup,
            amount0Min * self.slippage,
            amount1Min * self.slippage,
            deadline,
        )
        tx = self.nonfungible_position_manager.increaseLiquidity(params)

        liquidity_returned, amount0, amount1 = tx.return_value

        # printout after increasing
        print(f"Token ID: {token_id} status position post increasing liquidity...")
        position_after = print_position(self.nonfungible_position_manager, token_id)

        # include assert for liq increase & increase of fees earned
        assert (
            position_before["liquidity"] + liquidity_returned
            == position_after["liquidity"]
        )

        # greater or equal in case there was 0 swap activity in the pool
        assert position_after["tokensOwed0"] >= position_before["tokensOwed0"]
        assert position_after["tokensOwed1"] >= position_before["tokensOwed1"]

        # update the json file with new amounts and liquidity, given the token_id
        path = os.path.dirname("scripts/TCL/positionData/")
        directory = os.fsencode(path)

        for file in os.listdir(directory):
            file_name = os.fsdecode(file)

            if token_id in file_name:
                data = open(f"scripts/TCL/positionData/{file_name}")
                json_file = json.load(data)
                tx_detail_json = Path(f"scripts/TCL/positionData/{file_name}")

                with tx_detail_json.open("w") as fp:
                    tx_data = {
                        "tokenId": token_id,
                        "liquidity": json_file["liquidity"] + liquidity_returned,
                        "amount0": json_file["amount0"]
                        + amount0 / 10 ** token0.decimals(),
                        "amount1": json_file["amount1"]
                        + amount1 / 10 ** token1.decimals(),
                        "lowerTick": lower_tick,
                        "upperTick": upper_tick,
                    }
                    json.dump(tx_data, fp, indent=4, sort_keys=True)

    def mint_position(self, pool_addr, range0, range1, token0_amount, token1_amount):
        """
        Create a NFT on the desired range, adding the liquidity specified
        with the params `token0_amount` & `token1_amonunt`
        """
        # docs: https://docs.uniswap.org/protocol/reference/periphery/NonfungiblePositionManager#mint

        pool = interface.IUniswapV3Pool(pool_addr, owner=self.safe.account)

        token0 = self.safe.contract(pool.token0())
        token1 = self.safe.contract(pool.token1())

        if token0_amount > 0:
            token0.approve(self.nonfungible_position_manager, token0_amount)
        if token1_amount > 0:
            token1.approve(self.nonfungible_position_manager, token1_amount)

        decimals_diff = token1.decimals() - token0.decimals()

        # params for minting method
        lower_tick = int(math.log((1 / range1) * 10 ** decimals_diff, BASE) // 60 * 60)
        upper_tick = int(math.log((1 / range0) * 10 ** decimals_diff, BASE) // 60 * 60)
        deadline = chain.time() + self.deadline

        # calcs for min amounts
        sqrtRatioX96, currentTick, _, _, _, _, _ = pool.slot0()
        sqrtRatio_lower_tick = getSqrtRatioAtTick(lower_tick)
        sqrtRatio_upper_tick = getSqrtRatioAtTick(upper_tick)

        amount0Min = 0
        amount1Min = 0

        liquidity = maxLiquidityForAmounts(
            sqrtRatioX96,
            sqrtRatio_lower_tick,
            sqrtRatio_upper_tick,
            token0_amount,
            token1_amount,
        )

        if currentTick < lower_tick:
            # calc amount0Min
            amount0Min = getAmount0Delta(
                sqrtRatio_lower_tick, sqrtRatio_upper_tick, liquidity
            )
            amount1Min = 0
        elif currentTick < upper_tick:
            # calc both
            amount0Min = getAmount0Delta(sqrtRatioX96, sqrtRatio_upper_tick, liquidity)
            amount1Min = getAmount1Delta(sqrtRatio_lower_tick, sqrtRatioX96, liquidity)
        else:
            # calculate amount1Min
            amount0Min = 0
            amount1Min = getAmount1Delta(
                sqrtRatio_lower_tick, sqrtRatio_upper_tick, liquidity
            )

        # MintParams: https://docs.uniswap.org/protocol/reference/periphery/interfaces/INonfungiblePositionManager#mintparams
        tx = self.nonfungible_position_manager.mint(
            (
                token0.address,
                token1.address,
                3000,
                lower_tick,
                upper_tick,
                token0_amount,
                token1_amount,
                amount0Min * self.slippage,
                amount1Min * self.slippage,
                self.safe.address,
                deadline,
            )
        )
        # grabbing this data, despite that token_id may differ till tx gets signed/mined
        token_id, liquidity, amount0, amount1 = tx.return_value
        date = datetime.now().strftime("%Y-%m-%d")

        # drop this data into a json for records in this directory
        os.makedirs(f"scripts/TCL/positionData/", exist_ok=True)
        file_name = f"{token_id}_{date}"
        tx_detail_json = Path(f"scripts/TCL/positionData/{file_name}.json")
        with tx_detail_json.open("w") as fp:
            tx_data = {
                "tokenId": token_id,
                "liquidity": liquidity,
                "amount0": amount0 / 10 ** token0.decimals(),
                "amount1": amount1 / 10 ** token1.decimals(),
                "lowerTick": lower_tick,
                "upperTick": upper_tick,
            }
            json.dump(tx_data, fp, indent=4, sort_keys=True)

    def positions_info(self):
        nfts_owned = self.nonfungible_position_manager.balanceOf(self.safe) - 1

        if nfts_owned >= 0:
            with multicall:
                token_ids = [
                    self.nonfungible_position_manager.tokenOfOwnerByIndex(self.safe, i)
                    for i in range(nfts_owned)
                ]

            for token_id in token_ids:
                print("owner:", self.nonfungible_position_manager.ownerOf(token_id))
                print_position(self.nonfungible_position_manager, token_id)

                position = self.nonfungible_position_manager.positions(token_id)

                pool = self._get_pool(position)

                fees = calc_all_accum_fees(
                    self.nonfungible_position_manager, pool, token_id
                )

                token0 = self.safe.contract(position["token0"])
                token1 = self.safe.contract(position["token1"])

                print("accumulated fees:")
                print(fees[0] / 10 ** token0.decimals(), token0.symbol())
                print(fees[1] / 10 ** token1.decimals(), token1.symbol())
        else:
            print(f" === Safe ({self.safe.address}) does not own any NFT === ")

    def transfer_nft(self, token_id, new_owner):
        """
        transfer the targeted token_id to the new owner
        """
        # assert current owner
        assert self.nonfungible_position_manager.ownerOf(token_id) == self.safe.address

        self.nonfungible_position_manager.transferFrom(
            self.safe.address, new_owner, token_id
        )

        # assert new owner
        assert self.nonfungible_position_manager.ownerOf(token_id) == new_owner

    def swap(self, path, mantissa, destination=None):
        # https://docs.uniswap.org/protocol/guides/swaps/multihop-swaps
        destination = self.safe.address if not destination else destination

        token_in, token_out = path[0], path[-1]

        balance_token_out = token_out.balanceOf(self.safe)

        multihop_path = self._build_multihop_path(path)

        path_encoded = b""
        for item in multihop_path:
            if web3.isAddress(item):
                path_encoded += web3.toBytes(hexstr=item)
            else:
                path_encoded += int.to_bytes(item, 3, byteorder="big")

        min_out = self.quoter.quoteExactInput.call(path_encoded, mantissa) * (
            1 - self.slippage
        )

        params = (
            path_encoded,
            destination,
            web3.eth.getBlock(web3.eth.blockNumber).timestamp + self.deadline,
            mantissa,
            min_out,
        )

        token_in.approve(self.router, mantissa)

        tx = self.router.exactInput(params)

        assert token_out.balanceOf(destination) >= balance_token_out + min_out

        return tx.return_value
