from brownie import ZERO_ADDRESS
from pycoingecko import CoinGeckoAPI

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    aura = safe.contract(r.treasury_tokens.AURA)
    weth = safe.contract(r.treasury_tokens.WETH)
    graviaura = safe.contract(r.sett_vaults.graviAURA)
    aurabal = safe.contract(r.treasury_tokens.AURABAL)
    bal = safe.contract(r.treasury_tokens.BAL)
    wrapper = safe.contract(r.aura.wrapper)
    bpt_grav_weth_aura = safe.contract(r.balancer.bpt_33_grav_33_weth_33_aura)
    bpt_grav_weth_aurabal = safe.contract(r.balancer.bpt_33_grav_33_weth_33_aurabal)
    bpt_badger_grav = safe.contract(r.balancer.bpt_80_badger_20_grav)

    tokens = [
        aura, weth, graviaura, aurabal, bal, bpt_grav_weth_aura,
        bpt_grav_weth_aurabal, bpt_badger_grav
    ]

    safe.init_balancer()
    safe.balancer.get_pool_data(update_cache=True)
    safe.take_snapshot(tokens)

    ids = ['aura-finance', 'ethereum', 'balancer']
    prices =  CoinGeckoAPI().get_price(ids, 'usd')

    # calc amounts needed per token based on usd rate
    # 1 aurabal ~= 2.5 bal; adding .5x extra margin here
    bucket = 20_000e18 / 3
    usd_weth = int(bucket / prices['ethereum']['usd'])
    usd_aura = int(bucket / prices['aura-finance']['usd'])
    usd_aurabal = int(bucket / prices['balancer']['usd'] / 3)

    safe.balancer.swap(weth, bal, usd_weth * 1.1)

    # acquire necessary graviaura
    aura.approve(graviaura, usd_aura * 2)
    graviaura.deposit(usd_aura * 2)

    safe.balancer.deposit_and_stake(
        [graviaura, weth, aura],
        [usd_aura, usd_weth, usd_aura],
        pool=bpt_grav_weth_aura,
        stake=False,
        pool_type='Stable' # temp hack due to api not having pools available yet
    )

    # deposit bal via wrapper: bal -> 80bal20weth -> vebal -> aurabal
    # pass address(0) as stake to prevent minting for the depositor's contract:
    # https://etherscan.io/address/0xead792b55340aa20181a80d6a16db6a0ecd1b827#code#F33#L192
    dusty_bal = bal.balanceOf(safe) * .98
    bal.approve(wrapper, dusty_bal)
    wrapper.deposit(
        dusty_bal,  # uint256 _amount
        wrapper.getMinOut(dusty_bal, 9950),  # uint256 _minOut
        False,  # bool _lock
        ZERO_ADDRESS  # address _stakeAddress
    )

    safe.balancer.deposit_and_stake(
        [graviaura, weth, aurabal],
        [usd_aura, usd_weth, usd_aurabal],
        pool=bpt_grav_weth_aurabal,
        stake=False,
        pool_type='Stable' # temp hack due to api not having pools available yet
    )

    # clean up; send rest of aura to voter
    aura.transfer(
        r.badger_wallets.treasury_voter_multisig, aura.balanceOf(safe)
    )

    safe.post_safe_tx()
