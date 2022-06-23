from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    aura = safe.contract(r.treasury_tokens.AURA)
    weth = safe.contract(r.treasury_tokens.WETH)
    graviaura = safe.contract(r.sett_vaults.graviAURA)
    aurabal = safe.contract(r.treasury_tokens.AURABAL)
    badger = safe.contract(r.treasury_tokens.BADGER)
    bpt_grav_weth_aura = safe.contract(r.balancer.bpt_33_grav_33_weth_33_aura)
    bpt_grav_weth_aurabal = safe.contract(r.balancer.bpt_33_grav_33_weth_33_aurabal)
    bpt_badger_grav = safe.contract(r.balancer.bpt_80_badger_20_grav)

    tokens = [
        aura, weth, graviaura, aurabal, badger, bpt_grav_weth_aura,
        bpt_grav_weth_aurabal, bpt_badger_grav
    ]

    safe.init_balancer()
    safe.take_snapshot(tokens)

    safe.balancer.get_pool_data(update_cache=True)
    safe.balancer.deposit_and_stake(
        [graviaura, weth, aura], [0, 1e18, 0], pool=bpt_grav_weth_aura
    )
    safe.balancer.deposit_and_stake(
        [graviaura, weth, aurabal], [0, 1e18, 0], pool=bpt_grav_weth_aurabal
    )
    safe.balancer.deposit_and_stake(
        [graviaura, badger], [0, 1e18], pool=bpt_badger_grav
    )

    safe.post_safe_tx()
