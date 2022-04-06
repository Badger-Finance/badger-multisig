from rich.console import Console
from brownie import interface, chain, Contract, accounts
from helpers.addresses import registry

CONSOLE = Console()

# dxs tokens to liquidated
dxs_tokens = ["dxsWbtcWeth", "dxsBadgerWeth"]

DEADLINE = 60 * 60 * 12
MAX_SLIPPAGE = 0.02

ACCOUNT_TO_LOAD = ""


def main(broadcast="true"):
    dev = accounts.load(ACCOUNT_TO_LOAD)

    safe = interface.IMultisigWalletWithDailyLimit(
        registry.arbitrum.badger_wallets.dev_multisig_deprecated
    )

    router = Contract(registry.arbitrum.swapr.router)

    for key in dxs_tokens:
        slp = interface.IUniswapV2Pair(registry.arbitrum.treasury_tokens[f"{key}"])

        slp_balance = slp.balanceOf(safe)
        # 1. approve slp
        calldata_approve = slp.approve.encode_input(router.address, slp_balance)

        # 2. remove liq calldata_remove_liq = router.removeLiquidity()
        deadline = chain.time() + DEADLINE

        expected_asset0 = slp.getReserves()[0] * slp_balance / slp.totalSupply()
        expected_asset1 = slp.getReserves()[1] * slp_balance / slp.totalSupply()

        calldata_remove_liq = router.removeLiquidity.encode_input(
            slp.token0(),
            slp.token1(),
            slp_balance,
            expected_asset0 * (1 - MAX_SLIPPAGE),
            expected_asset1 * (1 - MAX_SLIPPAGE),
            safe.address,
            deadline,
        )

        CONSOLE.print(
            f" === Calldata for [green]{key}[/green] the approve=[blue]{calldata_approve}[/blue]. Target:[blue]{slp.address}[/blue] === \n"
        )
        CONSOLE.print(
            f" === Calldata for removing liquidity of [green]{key}[/green], calldata=[blue]{calldata_remove_liq}[/blue]. Target:[blue]{router.address}[/blue] === \n"
        )

        if broadcast == "true":
            safe.submitTransaction(slp.address, 0, calldata_approve, {"from": dev})
            safe.submitTransaction(
                router.address, 0, calldata_remove_liq, {"from": dev}
            )
