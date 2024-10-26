from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    voter.init_badger()

    hh_data = voter.badger.get_hh_data()

    # incentives tokens expected on epochs: $badger and/or $liquis
    rewards = [r.treasury_tokens.BADGER, r.treasury_tokens.LIQ]

    trops.take_snapshot(tokens=rewards)

    if len(hh_data) > 0:
        voter.badger.claim_bribes_hidden_hands(claim_from_strat=False)

    voter.badger.claim_bribes_from_paladin()

    for token in rewards:
        token = voter.contract(token)
        token_balance = token.balanceOf(voter)
        if token_balance > 0:
            token.transfer(trops, token_balance)

    trops.print_snapshot()
    voter.post_safe_tx()
