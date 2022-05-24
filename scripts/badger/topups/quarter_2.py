from decimal import Decimal

from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


N_WEEKS  = 6


def main():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    dripper = GreatApeSafe(registry.eth.drippers.tree_2022_q2)
    geyser = GreatApeSafe(registry.eth.badger_wallets.native_autocompounder)

    badger = interface.ERC20(
        registry.eth.treasury_tokens.BADGER, owner=trops.account
    )
    digg = interface.ERC20(
        registry.eth.treasury_tokens.DIGG, owner=trops.account
    )

    trops.take_snapshot([badger, digg])
    dripper.take_snapshot([badger, digg])
    geyser.take_snapshot([badger, digg])

    # badger emissions
    quarter_2_badger_emissions = Decimal(20_000e18) * N_WEEKS
    quarter_2_rembadger_emissions = Decimal(7692.307692e18) * N_WEEKS
    badger.transfer(
        dripper, quarter_2_badger_emissions + quarter_2_rembadger_emissions
    )

    # bdigg rewards
    trops.init_badger()
    weekly_digg_rewards = Decimal(trops.badger.from_gdigg_to_digg(2.5)) * 10**digg.decimals()
    # bdigg rewards will stop as per this week
    # catch up for last 5 weeks since last topup was 5 weeks ago;
    # 0xfa74dd997c4300f724f1f44414308f572588af16095a4c377cd700f592700316
    quarter_2_digg_emissions = weekly_digg_rewards * 5
    digg.transfer(geyser, quarter_2_digg_emissions)

    trops.print_snapshot()
    dripper.print_snapshot()
    geyser.print_snapshot()

    trops.post_safe_tx()
