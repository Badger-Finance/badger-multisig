from rich.console import Console
from helpers.addresses import registry
from great_ape_safe import GreatApeSafe
from brownie import interface, chain, Contract


CONSOLE = Console()


# curve params
SLIPPAGE_THRESHOLD_CURVE = 0.1

curve_target_wd = [
    "crvRenBTC",
    "crvTricrypto"
    ]


# sushi params
DEADLINE_SUSHI = 60 * 60 * 12
MAX_SLIPPAGE_SUSHI = 0.02

slp_tokens =[
    registry.arbitrum.treasury_tokens.slpWbtcEth,
    registry.arbitrum.treasury_tokens.slpSushiWeth,
    registry.arbitrum.treasury_tokens.slpCrvWeth
]

all_tokens_sushi = [
    [
        interface.IUniswapV2Pair(slp).token0(),
        interface.IUniswapV2Pair(slp).token1(),
        slp
    ] for slp in slp_tokens
]

all_tokens_sushi = [item for sublist in all_tokens_sushi for item in sublist]


# swapr params
DEADLINE_SWAPR = 60 * 60 * 12
MAX_SLIPPAGE_SWAPR = 0.02

dxs_tokens = [
    registry.arbitrum.treasury_tokens.dxsWbtcWeth,
    registry.arbitrum.treasury_tokens.dxsBadgerWeth,
    registry.arbitrum.treasury_tokens.dxsSwaprWeth,
    registry.arbitrum.treasury_tokens.dxsIbbtcWeth
]

all_tokens_swapr = [
    [
        interface.IUniswapV2Pair(slp).token0(),
        interface.IUniswapV2Pair(slp).token1(),
        slp
    ] for slp in dxs_tokens
]

all_tokens_swapr = [item for sublist in all_tokens_swapr for item in sublist]


def main():
    safe = GreatApeSafe(registry.arbitrum.badger_wallets.dev_multisig)

    router_sushi = safe.contract(registry.arbitrum.sushi.router)
    router_swapr = safe.contract(registry.arbitrum.swapr.router)

    bDXS = safe.contract(registry.arbitrum.sett_vaults.bdxsSwaprWeth)
    wbtc = registry.arbitrum.treasury_tokens.WBTC
    swpr = interface.ERC20(registry.arbitrum.treasury_tokens.SWPR, owner=safe.address)
    weth = registry.arbitrum.treasury_tokens.WETH

    tokens = list(set(all_tokens_sushi + all_tokens_swapr + [
        bDXS.address, wbtc, swpr.address, weth
    ]))
    safe.take_snapshot(tokens=tokens)


    # withdraw bDXS
    # reverts on fork: https://github.com/eth-brownie/brownie/issues/1537
    bDXS.withdrawAll()


    # withdraw curve lp to wbtc
    for key in curve_target_wd:
        lp_token = interface.IERC20(registry.arbitrum.treasury_tokens[key], owner=safe)

        pool = (
            interface.ICurvePoolV2(registry.arbitrum.crv_3_pools[key], owner=safe.address)
            if "Tricrypto" in key
            else interface.ICurvePool(registry.arbitrum.crv_pools[key], owner=safe.address)
        )

        lp_token_balance = lp_token.balanceOf(safe)

        coin_index = 1 if "Tricrypto" in key else 0

        min_withdraw_wbtc = pool.calc_withdraw_one_coin(lp_token_balance, coin_index)

        pool.remove_liquidity_one_coin(
            lp_token_balance, coin_index, min_withdraw_wbtc * (1 - SLIPPAGE_THRESHOLD_CURVE)
        )


    # sushi withdraw
    for address in slp_tokens:
        slp = interface.IUniswapV2Pair(address, owner=safe.address)

        slp_balance = slp.balanceOf(safe)
        if slp_balance <= 0:
            continue
        # 1. approve slp
        slp.approve(router_sushi.address, slp_balance)

        # 2. remove liq calldata_remove_liq = router.removeLiquidity()
        deadline = chain.time() + DEADLINE_SUSHI

        expected_asset0 = slp.getReserves()[0] * slp_balance / slp.totalSupply()
        expected_asset1 = slp.getReserves()[1] * slp_balance / slp.totalSupply()

        router_sushi.removeLiquidity(
            slp.token0(),
            slp.token1(),
            slp_balance,
            expected_asset0 * (1 - MAX_SLIPPAGE_SUSHI),
            expected_asset1 * (1 - MAX_SLIPPAGE_SUSHI),
            safe.address,
            deadline,
        )


    # swapr withdraw
    for address in dxs_tokens:
        slp = interface.IUniswapV2Pair(address, owner=safe.address)

        slp_balance = slp.balanceOf(safe)
        assert slp_balance > 0
        # 1. approve slp
        slp.approve(router_swapr.address, slp_balance)

        # 2. remove liq calldata_remove_liq = router.removeLiquidity()
        deadline = chain.time() + DEADLINE_SWAPR

        expected_asset0 = slp.getReserves()[0] * slp_balance / slp.totalSupply()
        expected_asset1 = slp.getReserves()[1] * slp_balance / slp.totalSupply()

        router_swapr.removeLiquidity(
            slp.token0(),
            slp.token1(),
            slp_balance,
            expected_asset0 * (1 - MAX_SLIPPAGE_SWAPR),
            expected_asset1 * (1 - MAX_SLIPPAGE_SWAPR),
            safe.address,
            deadline,
        )


    # swap swapr for eth
    path = [swpr.address, weth]
    amountIn = swpr.balanceOf(safe)
    deadline = chain.time() + DEADLINE_SWAPR
    amountOut = router_swapr.getAmountsOut(amountIn, path)[-1]

    swpr.approve(router_swapr.address, amountIn)

    # makes sense to send as destination to techops i guess directly
    router_swapr.swapExactTokensForETH(
        amountIn,
        amountOut * (1 - MAX_SLIPPAGE_SWAPR),
        path,
        registry.arbitrum.badger_wallets.techops_multisig,
        deadline,
    )

    safe.print_snapshot()
    safe.post_safe_tx(skip_preview=True)
