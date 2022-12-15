from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.techops_multisig)
    safe.init_opolis()

    work = safe.contract(r.coingecko_tokens.WORK)

    safe.take_snapshot(tokens=[work])

    safe.opolis.stake(work.balanceOf(safe))

    safe.print_snapshot()
    safe.post_safe_tx()
