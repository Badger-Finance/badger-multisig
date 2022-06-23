from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    safe.init_badger()

    bribes_dest = GreatApeSafe(safe.badger.strat_bvecvx.BRIBES_PROCESSOR())
    bribes_dest.take_snapshot(registry.eth.bribe_tokens_claimable.values())

    # Handling cvxFXS rewards as bribes (Ref: https://github.com/Badger-Finance/badger-strategies/issues/56)
    safe.badger.sweep_reward_token(registry.eth.bribe_tokens_claimable["cvxFXS"])

    safe.badger.claim_bribes_votium(registry.eth.bribe_tokens_claimable)
    safe.badger.claim_bribes_convex(registry.eth.bribe_tokens_claimable)

    bribes_dest.print_snapshot()

    safe.post_safe_tx(call_trace=True)
