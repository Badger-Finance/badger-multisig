from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    voting = safe.contract(r.aragon_voting)

    voting.vote(39, True, True)

    safe.post_safe_tx()
