from brownie import interface
from sympy import Symbol
from sympy.solvers import solve

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    """
    withdraw 9 digg from the slp_wbtcdigg tcl position to cover remaining
    emissions 2022-q1
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    wbtc = interface.ERC20(registry.eth.treasury_tokens.WBTC)
    digg = interface.ERC20(registry.eth.treasury_tokens.DIGG)
    slp_wbtcdigg = safe.contract(registry.eth.treasury_tokens.slpWbtcDigg)

    # expected_asset1 = slp.getReserves()[1] * slp_amount / slp.totalSupply()
    # solve for expected_asset1 = 9000000000
    x = Symbol('x')
    target = 9 * 10 ** digg.decimals()
    slp = slp_wbtcdigg
    mantissa_to_withdraw = solve(
        (slp.getReserves()[1] * x / slp.totalSupply()) - target, x
    )[0]

    tokens = [wbtc.address, digg.address, slp_wbtcdigg.address]

    trops.take_snapshot(tokens)
    safe.take_snapshot(tokens)
    safe.init_sushi()
    safe.sushi.remove_liquidity(slp_wbtcdigg, mantissa_to_withdraw, trops)
    safe.print_snapshot()
    trops.print_snapshot()
