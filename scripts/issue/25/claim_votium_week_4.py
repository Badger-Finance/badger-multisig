from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    candidates = registry.eth.bribe_tokens_claimable

    # current strat logic cannot handle ("protected asset")
    candidates.pop("CVX")

    # not eligible this week
    candidates.pop("BADGER")
    candidates.pop("MATIC")

    # not a votium candidate
    candidates.pop("NSBT")

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_badger()

    bribes_dest = GreatApeSafe(safe.badger.strat_bvecvx.BRIBES_RECEIVER())
    bribes_dest.take_snapshot(candidates.values())

    safe.badger.claim_bribes_votium(candidates)

    bribes_dest.print_snapshot()

    safe.post_safe_tx(post=False)
