from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    candidates_votium = registry.eth.bribe_tokens_claimable.copy()

    # claimed before and no new incentives this round
    candidates_votium.pop("BADGER")
    candidates_votium.pop("OGN")

    # not a votium candidate
    candidates_votium.pop("MATIC")
    candidates_votium.pop("NSBT")

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_badger()

    bribes_dest = GreatApeSafe(safe.badger.strat_bvecvx.BRIBES_RECEIVER())
    bribes_dest.take_snapshot(registry.eth.bribe_tokens_claimable.values())

    safe.badger.claim_bribes_votium(candidates_votium)
    safe.badger.claim_bribes_convex(registry.eth.bribe_tokens_claimable)

    bribes_dest.print_snapshot()

    safe.post_safe_tx(call_trace=True)
