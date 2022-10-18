from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)

    vlAURA = voter.contract(r.aura.vlAURA)

    _, unlockable, _, _ = vlAURA.lockedBalances(voter)

    if unlockable > 0:
        vlAURA.processExpiredLocks(True)

        _, unlockable, _, _ = vlAURA.lockedBalances(voter)
        assert unlockable == 0

        voter.post_safe_tx()
    else:
        print("============ CURRENTLY NO AURA IS UNLOCKABLE! ============")
