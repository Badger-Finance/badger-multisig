from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    voter.init_badger()

    rewards = [x["token"] for x in voter.badger.get_hh_data()]

    trops.take_snapshot(tokens=rewards)

    voter.badger.claim_bribes_hidden_hands(claim_from_strat=False)

    for token in rewards:
        token = voter.contract(token)
        token.transfer(trops, token.balanceOf(voter))

    trops.print_snapshot()
    voter.post_safe_tx()
