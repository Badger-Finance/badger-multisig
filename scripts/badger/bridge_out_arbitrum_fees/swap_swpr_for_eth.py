from rich.console import Console
from brownie import interface, chain, Contract, accounts
from helpers.addresses import registry

CONSOLE = Console()

DEADLINE = 60 * 60 * 12
MAX_SLIPPAGE = 0.02

ACCOUNT_TO_LOAD = ""


def main(broadcast="true"):
    dev = accounts.load(ACCOUNT_TO_LOAD)

    safe = interface.IMultisigWalletWithDailyLimit(
        registry.arbitrum.badger_wallets.dev_multisig_deprecated
    )

    router = Contract(registry.arbitrum.swapr.router)

    swpr = Contract(registry.arbitrum.treasury_tokens.SWPR)

    amountIn = swpr.balanceOf(safe)

    path = [swpr.address, registry.arbitrum.treasury_tokens.WETH]

    deadline = chain.time() + DEADLINE

    amountOut = router.getAmountsOut(amountIn, path)[-1]

    calldata_approve = swpr.approve.encode_input(router.address, amountIn)

    # makes sense to send as destination to techops i guess directly
    calldata_swap = router.swapExactTokensForETH.encode_input(
        amountIn,
        amountOut * (1 - MAX_SLIPPAGE),
        path,
        registry.arbitrum.badger_wallets.techops_multisig,
        deadline,
    )

    CONSOLE.print(
        f" === Calldata for [green]SWPR[/green] the approve=[blue]{calldata_approve}[/blue]. Target:[blue]{swpr.address}[/blue] === \n"
    )
    CONSOLE.print(
        f" === Calldata for swapping SWPR for ETH, calldata=[blue]{calldata_swap}[/blue]. Target:[blue]{router.address}[/blue] === \n"
    )

    if broadcast == "true":
        safe.submitTransaction(swpr.address, 0, calldata_approve, {"from": dev})
        safe.submitTransaction(router.address, 0, calldata_swap, {"from": dev})
