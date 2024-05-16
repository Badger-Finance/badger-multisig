from helpers.addresses import r
from brownie import interface, chain
from great_ape_safe import GreatApeSafe

TECHOPS = r.badger_wallets.techops_multisig
BREMBADGER = r.brembadger

def enable_deposits():
    safe = GreatApeSafe(TECHOPS)

    brembadger = safe.contract(BREMBADGER, interface.IbremBadger)
    brembadger.enableDeposits()
    assert brembadger.depositStart() == chain.time()

    safe.post_safe_tx()


def disable_deposits():
    safe = GreatApeSafe(TECHOPS)

    brembadger = safe.contract(BREMBADGER, interface.IbremBadger)
    brembadger.disableDeposits()
    assert brembadger.depositEnd() == chain.time()

    safe.post_safe_tx()