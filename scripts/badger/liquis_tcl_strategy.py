from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main(pendant_bunni_gauge_rewards=True):
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_liquis()
    vault.init_bunni()
    vault.init_balancer()

    # tokens
    weth = vault.contract(r.treasury_tokens.WETH)
    lit = vault.contract(r.bunni.LIT)
    liq = vault.contract(r.treasury_tokens.LIQ)

    # balancer pool
    bpt_lit_weth = vault.contract(r.balancer.B_80LIT_20_WETH)

    # rewards pool
    reward_pool = vault.contract(r.liquis.rewards_pool_309720_332580)

    # snap
    vault.take_snapshot(tokens=[weth, vault.bunni.olit, lit, liq])

    # liquis rewards claim
    reward_pool.getReward()

    if pendant_bunni_gauge_rewards:
        vault.bunni.claim_rewards(r.bunni.badger_wbtc_bunni_gauge_309720_332580)

    vault.bunni.exercise_olit()

    # swap lit -> weth
    lit_balance = lit.balanceOf(vault)
    vault.balancer.swap(lit, weth, lit_balance, pool=bpt_lit_weth)

    # TBD: processing of LIQ rewards

    vault.post_safe_tx()
