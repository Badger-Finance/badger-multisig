from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_bunni()
    vault.init_balancer()

    # tokens
    weth = vault.contract(r.treasury_tokens.WETH)
    lit = vault.contract(r.bunni.LIT)

    # balancer pool
    bpt_lit_weth = vault.contract(r.balancer.B_80LIT_20_WETH)

    # snap
    vault.take_snapshot(tokens=[weth, vault.bunni.olit, lit])

    vault.bunni.claim_rewards(r.bunni.badger_wbtc_bunni_gauge_309720_332580)
    # NOTE: explore olit rewards claim
    vault.print_snapshot()

    vault.bunni.exercise_olit()

    # swap lit -> weth
    lit_balance = lit.balanceOf(vault)
    vault.balancer.swap(lit, weth, lit_balance, pool=bpt_lit_weth)

    vault.post_safe_tx()
