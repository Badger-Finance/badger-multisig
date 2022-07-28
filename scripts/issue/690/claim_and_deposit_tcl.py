from pycoingecko import CoinGeckoAPI

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# THRESHOLDS FOR TARGET OPS
MAX_GRAVI_MANTISSA = 25_000e18
MAX_WBTC_MANTISSA = int(6.5e8)


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    vault.init_aura()
    vault.init_balancer()

    # tokens involved
    wbtc = vault.contract(r.treasury_tokens.WBTC)
    digg = vault.contract(r.treasury_tokens.DIGG)
    aura = vault.contract(r.treasury_tokens.AURA)
    bal = vault.contract(r.treasury_tokens.BAL)
    graviaura = vault.contract(r.sett_vaults.graviAURA)
    # https://app.balancer.fi/#/pool/0x8eb6c82c3081bbbd45dcac5afa631aac53478b7c000100000000000000000270
    bpt_40_wbtc_40_digg_20_graviaura = vault.contract(
        r.balancer.bpt_40wbtc_40digg_20graviaura
    )
    vault.take_snapshot([wbtc, digg, aura, bal, graviaura])
    voter.take_snapshot([bal, aura])

    # grab prices from coingecko
    ids = ["aura-finance", "wrapped-bitcoin", "digg"]
    prices = CoinGeckoAPI().get_price(ids, "usd")

    # claim rewards
    vault.aura.claim_all_from_booster()

    graviaura_bal = graviaura.balanceOf(vault)
    aura_bal = aura.balanceOf(vault)

    ppfs = graviaura.getPricePerFullShare() / 1e18
    aura_bal = aura.balanceOf(vault)
    graviaura_needed = MAX_GRAVI_MANTISSA - graviaura_bal
    aura_to_deposit = graviaura_needed * ppfs
    remaining_aura = aura_bal - aura_to_deposit

    # deposit aura into into graviaura to have at least 25k gravi available
    aura.approve(graviaura, aura_to_deposit)
    graviaura.deposit(aura_to_deposit)
    graviaura_mantissa = graviaura.balanceOf(vault)

    # send BAL and remaining of AURA
    bal.transfer(voter, bal.balanceOf(vault))
    aura.transfer(voter, remaining_aura)

    # deposit into target bpt (40WBTC_40DIGG_20GRAVIAURA)
    graviaura_usd_val = graviaura_mantissa / 1e18 * ppfs * prices["aura-finance"]["usd"]
    wbtc_mantissa = int(
        (graviaura_usd_val * 2 / prices["wrapped-bitcoin"]["usd"])
        * 10 ** wbtc.decimals()
    )
    digg_mantissa = int(
        (graviaura_usd_val * 2 / prices["digg"]["usd"]) * 10 ** digg.decimals()
    )
    if wbtc_mantissa > MAX_WBTC_MANTISSA:
        wbtc_mantissa = MAX_WBTC_MANTISSA

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

    # deposit&stake into aura the bpt
    rewards_contract = vault.contract(
        vault.aura.get_pool_info(bpt_40_wbtc_40_digg_20_graviaura)[3]
    )
    rewards_vault_bal = rewards_contract.balanceOf(vault)
    bpt_bal = bpt_40_wbtc_40_digg_20_graviaura.balanceOf(vault)
    vault.aura.deposit_all_and_stake(bpt_40_wbtc_40_digg_20_graviaura)
    assert rewards_contract.balanceOf(vault) == bpt_bal + rewards_vault_bal

    voter.print_snapshot()
    vault.post_safe_tx()
