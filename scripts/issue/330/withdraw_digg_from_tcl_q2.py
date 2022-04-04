from decimal import Decimal

from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    """
    withdraw gdigg from the slp_wbtcdigg tcl position to cover emissions
    for 2022-q2
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    wbtc = interface.ERC20(registry.eth.treasury_tokens.WBTC)
    digg = interface.IUFragments(registry.eth.treasury_tokens.DIGG)
    slp_wbtcdigg = safe.contract(registry.eth.treasury_tokens.slpWbtcDigg)

    safe.init_badger()
    # 13 weeks in q2
    total_mantissa = safe.badger.from_gdigg_to_digg(12.5 * 13) * Decimal(1e9)

    safe.init_sushi()
    mantissa_to_withdraw = safe.sushi.get_lp_to_withdraw_given_token(
        slp_wbtcdigg, digg, total_mantissa
    )

    tokens = [wbtc.address, digg.address, slp_wbtcdigg.address]

    trops.take_snapshot(tokens)
    safe.take_snapshot(tokens)
    assert mantissa_to_withdraw <= slp_wbtcdigg.balanceOf(safe)
    safe.sushi.remove_liquidity(slp_wbtcdigg, mantissa_to_withdraw, trops)
    safe.print_snapshot()
    trops.print_snapshot()
