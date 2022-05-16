from brownie import interface, chain
from helpers.addresses import registry
from great_ape_safe import GreatApeSafe


DEADLINE = 60 * 60 * 12
MAX_SLIPPAGE = 0.02


def main():
    safe = GreatApeSafe(registry.arbitrum.badger_wallets.dev_multisig)
    router = safe.contract(registry.arbitrum.swapr.router)
    swpr = interface.ERC20(registry.arbitrum.treasury_tokens.SWPR, owner=safe.address)
    weth = interface.ERC20(registry.arbitrum.treasury_tokens.WETH)

    safe.take_snapshot(tokens=[swpr, weth])

    path = [swpr.address, weth.address]
    amountIn = swpr.balanceOf(safe)
    deadline = chain.time() + DEADLINE
    amountOut = router.getAmountsOut(amountIn, path)[-1]

    swpr.approve(router.address, amountIn)

    # makes sense to send as destination to techops i guess directly
    router.swapExactTokensForETH(
        amountIn,
        amountOut * (1 - MAX_SLIPPAGE),
        path,
        registry.arbitrum.badger_wallets.techops_multisig,
        deadline,
    )

    safe.print_snapshot()
    safe.post_safe_tx()
