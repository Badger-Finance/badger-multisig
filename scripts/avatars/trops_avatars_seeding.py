import os

from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from pycoingecko import CoinGeckoAPI


cg = CoinGeckoAPI(os.getenv("COINGECKO_API_KEY"))

# dollar denominated
FUNDS_PER_POSITION = 20_000


def bpt_ratios_amounts(bpt, token0_rate, token1_rate, token0_decimals, token1_decimals):
    weights = bpt.getNormalizedWeights()
    ratio0 = weights[0] / 1e18
    ratio1 = weights[1] / 1e18

    return (
        int((FUNDS_PER_POSITION * ratio0 / token0_rate) * 10 ** token0_decimals),
        int((FUNDS_PER_POSITION * ratio1 / token1_rate) * 10 ** token1_decimals),
    )


def seed():
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    trops.init_balancer()
    trops.init_curve()

    # assets
    badger = trops.contract(r.treasury_tokens.BADGER)
    wbtc = trops.contract(r.treasury_tokens.WBTC)
    digg = trops.contract(r.treasury_tokens.DIGG)
    gravi = trops.contract(r.sett_vaults.graviAURA)
    weth = trops.contract(r.treasury_tokens.WETH)
    usdc = trops.contract(r.treasury_tokens.USDC)
    frax = trops.contract(r.treasury_tokens.FRAX)
    reth = trops.contract(r.treasury_tokens.RETH)

    # snap
    trops.take_snapshot(tokens=[badger, wbtc, weth, usdc])

    # decimals
    badger_decimals = badger.decimals()
    wbtc_decimals = wbtc.decimals()
    reth_decimals = reth.decimals()

    # balancer bpts
    bpt_wethreth = trops.contract(r.balancer.B_50_WETH_50_RETH)
    bpt_badgerwbtc = trops.contract(r.balancer.B_20_BTC_80_BADGER)
    bpt_badgerreth = trops.contract(r.balancer.B_50_BADGER_50_RETH)
    bpt_wbtcdigggravi = trops.contract(r.balancer.bpt_40wbtc_40digg_20graviaura)

    # convex lps
    pool_fraxbp = trops.contract(r.crv_factory_pools.badgerFRAXBP_f)
    badger_fraxbp = trops.contract(r.treasury_tokens.badgerFRAXBP_f_lp)
    wcvx_badger_fraxbp = trops.contract(r.convex.frax.wcvx_badger_fraxbp)
    fraxbp_zap = trops.contract(r.curve.zap_fraxbp)

    # pricing
    prices = cg.get_price(
        ids=["badger-dao", "wrapped-bitcoin", "weth", "rocket-pool-eth"],
        vs_currencies="usd",
    )
    badger_rate = prices["badger-dao"]["usd"]
    wbtc_rate = prices["wrapped-bitcoin"]["usd"]
    weth_rate = prices["weth"]["usd"]
    reth_rate = prices["rocket-pool-eth"]["usd"]

    # avatars
    aura_avatar = trops.contract(r.avatars.aura)
    convex_avatar = trops.contract(r.avatars.convex)

    # aura avatar deposits
    trops.balancer.deposit_and_stake(
        [wbtc, badger],
        bpt_ratios_amounts(
            bpt_badgerwbtc, wbtc_rate, badger_rate, wbtc_decimals, badger_decimals
        ),
        pool=bpt_badgerwbtc,
        stake=False,
    )

    weth_mantissa = int(((FUNDS_PER_POSITION // 2) / weth_rate) * 1e18 / 0.98)
    trops.balancer.swap(weth, reth, weth_mantissa, pool=bpt_wethreth)
    trops.balancer.deposit_and_stake(
        [badger, reth],
        bpt_ratios_amounts(
            bpt_badgerreth, badger_rate, reth_rate, badger_decimals, reth_decimals
        ),
        pool=bpt_badgerreth,
        stake=False,
    )

    # NOTE: for `bpt_wbtcdigggravi` acquisition prefer to avoid 2 swaps and simply deposit full amount in wbtc directly
    wbtc_amount = (FUNDS_PER_POSITION / wbtc_rate) * 10 ** wbtc_decimals
    trops.balancer.deposit_and_stake(
        [wbtc, digg, gravi],
        [wbtc_amount, 0, 0],
        pool=bpt_wbtcdigggravi,
        stake=False,
    )

    bpt_badgerwbtc_balance = bpt_badgerwbtc.balanceOf(trops)
    bpt_badgerreth_balance = bpt_badgerreth.balanceOf(trops)
    bpt_wbtcdigggravi_balancer = bpt_wbtcdigggravi.balanceOf(trops)

    bpt_badgerwbtc.approve(aura_avatar, bpt_badgerwbtc_balance)
    bpt_badgerreth.approve(aura_avatar, bpt_badgerreth_balance)
    bpt_wbtcdigggravi.approve(aura_avatar, bpt_wbtcdigggravi_balancer)
    aura_avatar.deposit(
        aura_avatar.getPids(),
        [bpt_badgerwbtc_balance, bpt_wbtcdigggravi_balancer, bpt_badgerreth_balance],
    )

    # convex avatar deposit
    trops.curve.deposit_zapper(
        fraxbp_zap,
        pool_fraxbp,
        [badger, frax, usdc],
        [
            ((FUNDS_PER_POSITION // 2) / badger_rate) * 1e18,
            0,
            (FUNDS_PER_POSITION // 2) * 1e6,
        ],
    )

    lp_balance = badger_fraxbp.balanceOf(trops)
    badger_fraxbp.approve(wcvx_badger_fraxbp, lp_balance)
    wcvx_badger_fraxbp.deposit(lp_balance, trops)

    staking_lp_balance = wcvx_badger_fraxbp.balanceOf(trops)
    assert staking_lp_balance == lp_balance

    wcvx_badger_fraxbp.approve(convex_avatar, staking_lp_balance)
    convex_avatar.depositInPrivateVault(
        convex_avatar.getPrivateVaultPids()[0], staking_lp_balance, False
    )

    trops.post_safe_tx()


def add_members():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)

    upkeep_manager = techops.contract(r.badger_wallets.upkeep_manager)

    upkeep_manager.addMember(
        r.avatars.aura,
        "AuraAvatar",
        # gas figure ref: https://github.com/Badger-Finance/badger-multisig/issues/1207#issuecomment-1490226452
        990_000,
        0,
    )

    upkeep_manager.addMember(
        r.avatars.convex,
        "ConvexAvatar",
        # gas figure ref: https://github.com/Badger-Finance/badger-multisig/issues/1207#issuecomment-1490226452
        5_007_000,
        0,
    )

    techops.post_safe_tx()
