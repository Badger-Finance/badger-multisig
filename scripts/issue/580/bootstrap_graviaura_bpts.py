from pycoingecko import CoinGeckoAPI

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    aura = safe.contract(r.treasury_tokens.AURA)
    weth = safe.contract(r.treasury_tokens.WETH)
    graviaura = safe.contract(r.sett_vaults.graviAURA)
    aurabal = safe.contract(r.treasury_tokens.AURABAL)
    badger = safe.contract(r.treasury_tokens.BADGER)
    bal = safe.contract(r.treasury_tokens.BAL)
    bpt_grav_weth_aura = safe.contract(r.balancer.bpt_33_grav_33_weth_33_aura)
    bpt_grav_weth_aurabal = safe.contract(r.balancer.bpt_33_grav_33_weth_33_aurabal)
    bpt_badger_grav = safe.contract(r.balancer.bpt_80_badger_20_grav)

    tokens = [
        aura, weth, graviaura, aurabal, badger, bal, bpt_grav_weth_aura,
        bpt_grav_weth_aurabal, bpt_badger_grav
    ]

    safe.init_balancer()
    safe.take_snapshot(tokens)

    ids = ['aura-finance', 'ethereum', 'balancer', 'badger-dao']
    prices =  CoinGeckoAPI().get_price(ids, 'usd')

    bucket = 20_000e18 / 3
    usd_weth = int(bucket / prices['ethereum']['usd'])
    usd_aura = int(bucket / prices['aura-finance']['usd'])
    usd_bal = int(bucket / prices['balancer']['usd'])
    bucket = 20_000e18 / 5
    usd_badger = int(bucket / prices['badger-dao']['usd']) * 4
    usd_gravi = int(bucket / prices['aura-finance']['usd'])

    print([usd_aura, usd_weth, usd_aura])
    print([usd_aura, usd_weth, usd_bal])
    print([usd_gravi, usd_badger])

    print('needed aura:', usd_aura * 4, (usd_aura * 4) / 1e18)
    print('needed weth:', usd_weth * 2, (usd_weth * 2) / 1e18)
    print('needed bal:', usd_bal, usd_bal / 1e18)
    print('needed badger:', usd_badger, usd_badger / 1e18)

    safe.balancer.swap(weth, aura, 40e18)
    safe.balancer.swap(weth, bal, 7e18)

    aura.approve(graviaura, usd_aura + usd_aura + usd_gravi)
    graviaura.deposit(usd_aura + usd_aura + usd_gravi)

    safe.print_snapshot()

    safe.balancer.get_pool_data(update_cache=True)
    safe.balancer.deposit_and_stake(
        [graviaura, weth, aura],
        [usd_aura, usd_weth, usd_aura],
        pool=bpt_grav_weth_aura,
        stake=False,
        pool_type='Stable' # temp hack due to api not having pools available yet
    )

    safe.print_snapshot()

    safe.balancer.deposit_and_stake(
        [graviaura, weth, aurabal],
        [usd_aura, usd_weth, usd_bal],
        pool=bpt_grav_weth_aurabal,
        pool_type='Stable' # temp hack due to api not having pools available yet
    )
    # safe.balancer.deposit_and_stake(
    #     [graviaura, badger],
    #     [usd_gravi, usd_badger],
    #     pool=bpt_badger_grav,
    #     pool_type='Stable' # temp hack due to api not having pools available yet
    # )

    safe.post_safe_tx()
