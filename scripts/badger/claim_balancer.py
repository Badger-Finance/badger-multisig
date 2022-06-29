from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    wbtc = safe.contract(r.treasury_tokens.WBTC)
    badger = safe.contract(r.treasury_tokens.BADGER)
    bal = safe.contract(r.treasury_tokens.BAL)

    safe.take_snapshot([wbtc, badger, bal])
    safe.init_balancer()
    safe.balancer.claim([wbtc, badger])
    safe.post_safe_tx()
