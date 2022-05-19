from decimal import Decimal

from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    tree = GreatApeSafe(registry.eth.badger_wallets.badgertree)

    badger = interface.ERC20(
        registry.eth.treasury_tokens.BADGER, owner=trops.account
    )

    digg = interface.ERC20(
        registry.eth.treasury_tokens.DIGG, owner=trops.account
    )

    trops.take_snapshot([badger, digg])
    tree.take_snapshot([badger, digg])

    # badger emissions
    week_20_badger_emissions = Decimal(20_000e18)
    week_20_rembadger_emissions = Decimal(7692.307692e18)

    badger.transfer(
        tree, week_20_badger_emissions + week_20_rembadger_emissions
    )

    # digg emissions
    week_19_digg_emissions_tree = Decimal(1.302461219e9)
    digg.transfer(tree, week_19_digg_emissions_tree)

    trops.print_snapshot()
    tree.print_snapshot()
    trops.post_safe_tx()
