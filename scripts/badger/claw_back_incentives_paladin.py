from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    safe.init_badger()

    # tokens
    liq = safe.contract(r.treasury_tokens.LIQ)
    badger = safe.contract(r.treasury_tokens.BADGER)

    # snap
    safe.take_snapshot(tokens=[badger, liq])

    # check if there are claimable withdrawable incentives in paladin
    safe.badger.claw_back_incentives_from_paladin()

    safe.post_safe_tx()
