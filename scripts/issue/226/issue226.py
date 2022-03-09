from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface


COLLATERAL_FACTOR = 0.5


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_rari()

    fbveCVX = interface.IFToken(registry.eth.rari['fbveCVX-22'])
    safe.rari.add_ftoken_to_pool(fbveCVX)
    safe.rari.ftoken_pause(fbveCVX)

    safe.post_safe_tx()
