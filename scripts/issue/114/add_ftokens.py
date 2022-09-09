from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface


COLLATERAL_FACTOR = 0.75 * 1e18


def main():
    """
    add fDOLA and fFRAX to our fuse-22 rari pool.
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_rari()

    fFRAX = interface.IFToken(registry.eth.rari["fFRAX-22"])
    fDOLA = interface.IFToken(registry.eth.rari["fDOLA-22"])

    safe.rari.add_ftoken_to_pool(fFRAX, cf=COLLATERAL_FACTOR)
    safe.rari.add_ftoken_to_pool(fDOLA, cf=COLLATERAL_FACTOR)

    safe.post_safe_tx()
