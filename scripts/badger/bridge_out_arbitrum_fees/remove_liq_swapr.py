from brownie import interface, chain
from helpers.addresses import registry
from great_ape_safe import GreatApeSafe


# dxs tokens to liquidated
dxs_tokens = [
    registry.arbitrum.treasury_tokens.dxsWbtcWeth,
    registry.arbitrum.treasury_tokens.dxsBadgerWeth,
    registry.arbitrum.treasury_tokens.dxsSwaprWeth,
    registry.arbitrum.treasury_tokens.dxsIbbtcWeth
    ]

all_tokens = [[interface.IUniswapV2Pair(slp).token0(),
              interface.IUniswapV2Pair(slp).token1(), slp] for slp in
              dxs_tokens]
# flatten
all_tokens = [item for sublist in all_tokens for item in sublist]


DEADLINE = 60 * 60 * 12
MAX_SLIPPAGE = 0.02


def main():
    safe = GreatApeSafe(registry.arbitrum.badger_wallets.dev_multisig)
    router = safe.contract(registry.arbitrum.swapr.router)
    safe.take_snapshot(tokens=all_tokens)

    for address in dxs_tokens:
        slp = interface.IUniswapV2Pair(address, owner=safe.address)

        slp_balance = slp.balanceOf(safe)
        assert slp_balance > 0
        # 1. approve slp
        slp.approve(router.address, slp_balance)

        # 2. remove liq calldata_remove_liq = router.removeLiquidity()
        deadline = chain.time() + DEADLINE

        expected_asset0 = slp.getReserves()[0] * slp_balance / slp.totalSupply()
        expected_asset1 = slp.getReserves()[1] * slp_balance / slp.totalSupply()

        router.removeLiquidity(
            slp.token0(),
            slp.token1(),
            slp_balance,
            expected_asset0 * (1 - MAX_SLIPPAGE),
            expected_asset1 * (1 - MAX_SLIPPAGE),
            safe.address,
            deadline,
        )

    safe.print_snapshot()
    safe.post_safe_tx()