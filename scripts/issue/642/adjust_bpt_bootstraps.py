from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)

    bpt_aura = safe.contract(r.balancer.bpt_33_grav_33_weth_33_aura)
    bpt_aurabal = safe.contract(r.balancer.bpt_33_grav_33_weth_33_aurabal)

    safe.init_balancer()
    safe.init_aura()
    tokens = [
        bpt_aura,
        bpt_aurabal,
        r.treasury_tokens.AURA,
        r.treasury_tokens.AURABAL,
        r.treasury_tokens.WETH,
        r.sett_vaults.graviAURA,
        safe.aura.booster.poolInfo(safe.aura.get_pool_info(bpt_aurabal)[0])[3]
    ]
    safe.take_snapshot(tokens)
    vault.take_snapshot(tokens)

    safe.balancer.unstake_all_and_withdraw_all(
        pool=bpt_aura,
        pool_type='non_stable',
        destination=r.badger_wallets.treasury_vault_multisig
    )
    safe.balancer.unstake_all_and_withdraw_all(
        pool=bpt_aurabal,
        pool_type='non_stable',
        destination=r.badger_wallets.treasury_vault_multisig
    )

    vault.print_snapshot()
    safe.post_safe_tx()
