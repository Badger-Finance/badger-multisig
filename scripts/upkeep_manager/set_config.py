from great_ape_safe import GreatApeSafe
from helpers.addresses import r


techops = GreatApeSafe(r.badger_wallets.techops_multisig)

# contract
upkeep_manager = techops.contract(r.badger_wallets.upkeep_manager)


def cancel_member(targert_member=r.safe_modules.treasury_voter.aura_auto_lock):
    """
    Cancels a member's Upkeep job
    """
    members = upkeep_manager.getMembers()
    assert targert_member in members

    upkeep_manager.cancelMemberUpkeep(targert_member)

    techops.post_safe_tx()


def set_min_rounds_topup(rounds=0):
    """
    Updates the value of `minRoundsTopUp`, which is used to decide if `UpkeepId` is underfunded
    """
    rounds = int(rounds)
    assert upkeep_manager.minRoundsTopUp() != rounds

    upkeep_manager.setMinRoundsTopUp(rounds)

    techops.post_safe_tx()


def set_rounds_topup(rounds=0):
    """
    Updates the value of `roundsTopUp`, which is used for decided
    how much rounds will be covered at least while topping-up
    """
    rounds = int(rounds)
    assert upkeep_manager.roundsTopUp() != rounds

    upkeep_manager.setRoundsTopUp(rounds)

    techops.post_safe_tx()


def pause():
    """
    Prevents executing `performUpkeep`
    """
    upkeep_manager.pause()

    techops.post_safe_tx()


def unpause():
    """
    Back to normal `performUpkeep` ops
    """
    upkeep_manager.unpause()

    techops.post_safe_tx()
