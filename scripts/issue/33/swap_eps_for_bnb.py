from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.bsc.badger_wallets.dev_multisig)

    safe.take_snapshot(tokens=[registry.bsc.airdropable_tokens.EPS])

    safe.init_pancakeswap_v2()

    eps = safe.contract(registry.bsc.airdropable_tokens.EPS)

    path = [eps.address, registry.bsc.treasury_tokens.WBNB]
    
    # only will be run when buffer eps is available and not distributions tokens are idle in the dev_msig
    safe.pancakeswap_v2.swap_exact_tokens_for_eth(eps, eps.balanceOf(safe), path, safe)

    safe.post_safe_tx()
