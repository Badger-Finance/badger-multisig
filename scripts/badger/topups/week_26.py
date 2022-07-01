from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    badger = interface.ERC20(registry.eth.treasury_tokens.BADGER, owner=trops.account)

    trops.take_snapshot([badger])

    # mainly to cover the deficit being created on the past weeks from graviAURA emissions
    badger.transfer(registry.eth.badger_wallets.badgertree, 6_000e18)

    trops.post_safe_tx()
