from decimal import Decimal

from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


N_WEEKS  = 6


def main():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    dripper = GreatApeSafe(registry.eth.drippers.rembadger_2022_q2)

    badger = interface.ERC20(
        registry.eth.treasury_tokens.BADGER, owner=trops.account
    )
    digg = interface.ERC20(
        registry.eth.treasury_tokens.DIGG, owner=trops.account
    )

    trops.take_snapshot([badger, digg])
    dripper.take_snapshot([badger, digg])

    # badger emissions
    quarter_2_badger_emissions = Decimal(20_000e18) * N_WEEKS
    quarter_2_rembadger_emissions = Decimal(7692.307692e18) * N_WEEKS
    badger.transfer(
        dripper, quarter_2_badger_emissions + quarter_2_rembadger_emissions
    )

    # digg emissions
    quarter_2_digg_emissions = Decimal(1.302461219e9) * N_WEEKS
    digg.transfer(dripper, quarter_2_digg_emissions)

    trops.print_snapshot()
    dripper.print_snapshot()

    trops.post_safe_tx()
