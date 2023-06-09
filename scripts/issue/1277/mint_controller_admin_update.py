from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)

    # contracts
    controller = safe.contract(r.GatedMiniMeController)
    timelock_gov = safe.contract(r.governance_timelock)

    controller.transferOwnership(timelock_gov)

    # guardian setup
    timelock_gov.setGuardian(r.badger_wallets.techops_multisig)

    safe.post_safe_tx()
