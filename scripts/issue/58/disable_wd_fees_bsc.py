from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    """
    set withdrawal fees to 0 on all three bsc setts
    """
    ops = GreatApeSafe(registry.bsc.badger_wallets.ops_multisig)
    for addr in registry.bsc.strategies.values():
        strat = interface.IStrategy(addr, owner=ops.account)
        strat.setWithdrawalFee(0)
    ops.post_safe_tx()
