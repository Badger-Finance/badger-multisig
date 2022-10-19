from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    destination = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    voter.init_badger()

    vlAURA = voter.contract(r.aura.vlAURA)
    AURABAL = voter.contract(r.treasury_tokens.AURABAL)
    GRAVI = voter.contract(r.sett_vaults.graviAURA)
    AURA = voter.contract(r.treasury_tokens.AURA)

    data = voter.badger.get_hh_data()
    rewards = [x["token"] for x in data]

    voter.take_snapshot(tokens=rewards)
    destination.take_snapshot(tokens=rewards)

    voter.badger.claim_bribes_hidden_hands(claim_from_strat=False)

    voter.print_snapshot()

    for token in rewards:
        token = voter.contract(token)
        token_balance = token.balanceOf(voter)
        if token_balance > 0:
            token.transfer(destination, token_balance)

    # add relock chore
    _, unlockable, _, _ = vlAURA.lockedBalances(voter)
    if unlockable > 0:
        vlAURA.processExpiredLocks(True)

        _, unlockable, _, _ = vlAURA.lockedBalances(voter)
        assert unlockable == 0

    # claim rewards and send to trops
    vlAURA.getReward(voter)
    AURABAL.transfer(destination, AURABAL.balanceOf(voter))

    # wd from gravi and lock aura. gravi is coming as fee os processing bribes
    gravi_balance = GRAVI.balanceOf(voter)
    if gravi_balance > 0:
        GRAVI.withdrawAll()
        aura_balance = AURA.balanceOf(voter)
        AURA.approve(vlAURA, aura_balance)
        vlAURA.lock(voter, aura_balance)

    destination.print_snapshot()
    voter.post_safe_tx()
