from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    safe.init_badger()

    bribes_dest = GreatApeSafe(safe.badger.strat_bvecvx.BRIBES_RECEIVER())
    bribes_dest.take_snapshot(registry.eth.bribe_tokens_claimable.values())

    safe.badger.claim_bribes_votium(registry.eth.bribe_tokens_claimable)
    safe.badger.claim_bribes_convex(registry.eth.bribe_tokens_claimable)

    bribes_dest.print_snapshot()

    safe.post_safe_tx(call_trace=True)
