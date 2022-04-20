from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():

    safe = GreatApeSafe(registry.bsc.badger_wallets.dev_multisig)
    eps = safe.contract(registry.bsc.airdropable_tokens.EPS)
    wbnb = safe.contract(registry.bsc.treasury_tokens.WBNB)

    safe.take_snapshot([eps])

    safe.init_pancakeswap_v2()
    safe.pancakeswap_v2.swap_exact_tokens_for_eth(eps, eps.balanceOf(safe), [eps, wbnb])

    safe.print_snapshot()
    safe.post_safe_tx()
