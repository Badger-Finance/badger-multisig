from pycoingecko import CoinGeckoAPI

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def migrate():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    # init sushi, bal and aura
    vault.init_sushi()
    vault.init_balancer()
    vault.init_aura()

    # tokens involved
    bal = vault.contract(r.treasury_tokens.BAL)
    aura = vault.contract(r.treasury_tokens.AURA)
    graviaura = vault.contract(r.sett_vaults.graviAURA)
    slp = vault.contract(r.treasury_tokens.slpWbtcDigg)
    wbtc = vault.contract(r.treasury_tokens.WBTC)
    digg = vault.contract(r.treasury_tokens.DIGG)
    # https://app.balancer.fi/#/pool/0x8eb6c82c3081bbbd45dcac5afa631aac53478b7c000100000000000000000270
    bpt_40_wbtc_40_digg_20_graviaura = vault.contract(
        r.balancer.bpt_40wbtc_40digg_20graviaura
    )

    vault.take_snapshot(tokens=[slp, graviaura, wbtc, digg, aura, bal])

    # grab prices from coingecko
    ids = ["aura-finance", "wrapped-bitcoin", "digg"]
    prices = CoinGeckoAPI().get_price(ids, "usd")

    # remove sushi tcl
    vault.sushi.remove_liquidity(slp, slp.balanceOf(vault))

    # claim aura rewards
    vault.aura.claim_all_from_booster()

    # deposit in graviaura and sent BAL claim to voter
    aura.approve(graviaura, 2 ** 256 - 1)
    graviaura.depositAll()
    aura.approve(graviaura, 0)
    bal.transfer(r.badger_wallets.treasury_voter_multisig, bal.balanceOf(vault))

    # deposit in balancer 40wbtc-40digg-20graviaura pool
    graviaura_mantissa = graviaura.balanceOf(vault)
    graviaura_usd_val = (
        graviaura_mantissa
        / 1e18
        * (graviaura.getPricePerFullShare() / 1e18)
        * prices["aura-finance"]["usd"]
    )
    wbtc_mantissa = int(
        (graviaura_usd_val * 2 / prices["wrapped-bitcoin"]["usd"])
        * 10 ** wbtc.decimals()
    )
    digg_mantissa = int(
        (graviaura_usd_val * 2 / prices["digg"]["usd"]) * 10 ** digg.decimals()
    )
    # print to cross-check: mantissas and usd token values
    print(
        "[wbtc_mantissa, digg_mantissa, graviaura_mantissa]",
        f"[{wbtc_mantissa}, {digg_mantissa}, {graviaura_mantissa}]",
    )
    print(
        "[wbtc_usd, digg_usd, aura_price]",
        f"[{prices['wrapped-bitcoin']['usd']}, {prices['digg']['usd']}, {prices['aura-finance']['usd']}]",
    )

    vault.balancer.deposit_and_stake(
        [wbtc, digg, graviaura],
        [wbtc_mantissa, digg_mantissa, graviaura_mantissa],
        pool=bpt_40_wbtc_40_digg_20_graviaura,
        stake=False,
        pool_type="non_stable",
    )

    # stake in AURA
    rewards_contract = vault.contract(
        vault.aura.get_pool_info(bpt_40_wbtc_40_digg_20_graviaura)[3]
    )
    bpt_bal = bpt_40_wbtc_40_digg_20_graviaura.balanceOf(vault)
    vault.aura.deposit_all_and_stake(bpt_40_wbtc_40_digg_20_graviaura)
    assert rewards_contract.balanceOf(vault) == bpt_bal

    vault.post_safe_tx()


def graviaura_transfer():
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    graviaura = voter.contract(r.sett_vaults.graviAURA)
    aura = voter.contract(r.treasury_tokens.AURA)

    graviaura.transfer(
        r.badger_wallets.treasury_vault_multisig, graviaura.balanceOf(voter)
    )
    aura.transfer(r.badger_wallets.treasury_vault_multisig, aura.balanceOf(voter))

    voter.post_safe_tx()
