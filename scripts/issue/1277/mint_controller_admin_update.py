from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)

    # contracts
    controller = safe.contract(r.controllers.minting)

    controller.transferOwnership(r.governance_timelock)

    safe.post_safe_tx()
