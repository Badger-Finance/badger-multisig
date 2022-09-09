from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main(destination="0x042B32Ac6b453485e357938bdC38e0340d4b9276"):  # trops
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    destination = GreatApeSafe(destination)
    voter.init_badger()

    data = voter.badger.get_hh_data()
    rewards = [x["token"] for x in data]

    voter.take_snapshot(tokens=rewards)
    destination.take_snapshot(tokens=rewards)

    voter.badger.claim_bribes_hidden_hands(claim_from_strat=False)

    voter.print_snapshot()

    for token in rewards:
        token = voter.contract(token)
        token.transfer(destination, token.balanceOf(voter))

    destination.print_snapshot()
    voter.post_safe_tx()
