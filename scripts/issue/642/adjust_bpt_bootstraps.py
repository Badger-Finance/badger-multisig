from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)

    bpt_aura = safe.contract(r.balancer.bpt_33_grav_33_weth_33_aura)
    bpt_aurabal = safe.contract(r.balancer.bpt_33_grav_33_weth_33_aurabal)

    safe.init_balancer()
    tokens = [
        bpt_aura,
        bpt_aurabal,
        r.treasury_tokens.AURA,
        r.treasury_tokens.AURABAL,
        r.treasury_tokens.WETH,
        r.sett_vaults.graviAURA,
        safe.balancer.gauge_factory.getPoolGauge(bpt_aura),
        safe.balancer.gauge_factory.getPoolGauge(bpt_aurabal)
    ]
    safe.take_snapshot(tokens)
    voter.take_snapshot(tokens)

    safe.balancer.unstake_all_and_withdraw_all(
        pool=bpt_aura,
        pool_type='non_stable',
        destination=r.badger_wallets.treasury_voter_multisig
    )
    safe.balancer.stake_all(bpt_aurabal)

    voter.print_snapshot()
    safe.post_safe_tx()
