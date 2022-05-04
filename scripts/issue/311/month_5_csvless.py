from decimal import Decimal

from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    dripper = GreatApeSafe(registry.eth.drippers.rembadger_2022_q2)

    badger = interface.ERC20(
        registry.eth.treasury_tokens.BADGER, owner=safe.account
    )

    safe.take_snapshot([badger])
    trops.take_snapshot([badger])
    dripper.take_snapshot([badger])

    # https://github.com/Badger-Finance/badger-multisig/issues/311#issuecomment-1108524915
    badger.transfer(trops, 150_000e18)
    badger.transfer(dripper, Decimal(51_913.076921) * Decimal(1e18))

    safe.print_snapshot()
    trops.print_snapshot()
    dripper.print_snapshot()

    safe.post_safe_tx()
