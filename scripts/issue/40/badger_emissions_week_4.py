from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


EMISSIONS = 73_572


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    tree = GreatApeSafe(registry.eth.badger_wallets.badgertree)

    badger = interface.ERC20(
        registry.eth.treasury_tokens.BADGER, owner=safe.account
    )

    safe.take_snapshot([badger.address])
    tree.take_snapshot([badger.address])

    badger.transfer(tree, EMISSIONS * 1e18)

    safe.print_snapshot()
    tree.print_snapshot()

    safe.post_safe_tx()
