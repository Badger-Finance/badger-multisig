from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)

    # contracts
    escrow = safe.contract(r.liquis.liq_vested_escrow)

    # tokens
    liq = safe.contract(r.treasury_tokens.LIQ)

    trops.take_snapshot([liq])

    escrow.claim(False)

    liq_balance = liq.balanceOf(safe.address)
    liq.transfer(r.badger_wallets.treasury_ops_multisig, liq_balance)

    trops.print_snapshot()
    safe.post_safe_tx()
