from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    badger = interface.ERC20(registry.eth.treasury_tokens.BADGER, owner=trops.account)

    trops.take_snapshot([badger])

    # covers the 25k directed for bootstrapping graviAURA program
    badger.transfer(registry.eth.drippers.tree_2022_q3, 25_000e18)

    # covers 40k badger tree deficit. Currently: ~194k at 1pm UTC, 1st July-2022
    # ~25k will be sent from tree_2022_q2 on the following tx, reducing deficit to ~129k
    badger.transfer(registry.eth.badger_wallets.badgertree, 40_000e18)

    trops.post_safe_tx()
