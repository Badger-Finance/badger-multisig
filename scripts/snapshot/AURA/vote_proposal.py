from great_ape_safe import GreatApeSafe
from helpers.addresses import r


GAUGE_TARGET = "80/20 BADGER/WBTC"
VOTE_WEIGHT = 1 # 100%


def main(
    proposal_id="0x515649bddfb0e0d637745e8654616b03b371bb444f90f327064e7eee6052aff8",
):
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    voter.init_snapshot(proposal_id)

    voter.snapshot.vote_and_post({GAUGE_TARGET: VOTE_WEIGHT})
