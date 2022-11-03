from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)

    aura_locker = voter.contract(r.aura.vlAURA)

    aura_locker.delegate(voter)

    voter.post_safe_tx()
