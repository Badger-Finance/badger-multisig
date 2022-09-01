from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from enum import Enum
 
 
class Gauges(Enum):
    badger = {"80/20 BADGER/WBTC": 1}
    digg = {"40/40/20 WBTC/DIGG/graviAURA": 1}
    graviaura = {"33/33/33 graviAURA/auraBAL/WETH": 1}


def main(
    proposal_id="0x515649bddfb0e0d637745e8654616b03b371bb444f90f327064e7eee6052aff8",
    gauge="badger"
):
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    voter.init_snapshot(proposal_id)

    voter.snapshot.vote_and_post(Gauges[gauge].value)
