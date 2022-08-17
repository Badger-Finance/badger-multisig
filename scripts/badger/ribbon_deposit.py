from great_ape_safe import GreatApeSafe
from helpers.addresses import r


MANTISSA = 100_000e18


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    badger = safe.contract(r.treasury_tokens.BADGER)
    ribbon_vault = safe.contract(r.ribbon.badger_vault)

    safe.take_snapshot([badger])

    badger.approve(ribbon_vault, MANTISSA)
    ribbon_vault.deposit(MANTISSA)

    safe.post_safe_tx(call_trace=True)
