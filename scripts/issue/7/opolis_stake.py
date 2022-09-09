from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface


def main():
    safe = GreatApeSafe(registry.poly.badger_wallets.ops_multisig)
    safe.init_opolis()

    safe.take_snapshot(tokens=[safe.opolis.work])

    # address must be whitelisted from opolis to stake
    assert safe.opolis.whitelist.isWhitelisted(safe)

    # stake full balance of WORK on opolis
    bal = safe.opolis.work.balanceOf(safe)
    safe.opolis.stake(bal)

    safe.post_safe_tx()
