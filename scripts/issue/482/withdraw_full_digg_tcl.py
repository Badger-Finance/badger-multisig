from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    """
    withdraw the whole slp_wbtcdigg tcl position.
    """

    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    wbtc = interface.ERC20(registry.eth.treasury_tokens.WBTC)
    digg = interface.ERC20(registry.eth.treasury_tokens.DIGG)
    slp_wbtcdigg = vault.contract(registry.eth.treasury_tokens.slpWbtcDigg)

    tokens = [wbtc.address, digg.address, slp_wbtcdigg.address]

    trops.take_snapshot(tokens)
    vault.take_snapshot(tokens)

    vault.init_sushi()
    mantissa = slp_wbtcdigg.balanceOf(vault)
    vault.sushi.remove_liquidity(slp_wbtcdigg, mantissa, trops)

    vault.print_snapshot()
    trops.print_snapshot()

    vault.post_safe_tx()
