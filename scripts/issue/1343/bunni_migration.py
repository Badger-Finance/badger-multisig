from great_ape_safe import GreatApeSafe
from helpers.addresses import r

from pycoingecko import CoinGeckoAPI

TREASURY_LIQ_TARGET = 500_000


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)

    # tokens
    badger = vault.contract(r.treasury_tokens.BADGER)
    wbtc = vault.contract(r.treasury_tokens.WBTC)

    vault.take_snapshot(tokens=[badger, wbtc])

    vault.init_bunni(r.bunni.badger_wbtc_bunni_token_309720_325620)

    # 1. wd from out-of-range pos
    vault.bunni.unstake(r.bunni.badger_wbtc_bunni_gauge_309720_325620)
    vault.bunni.withdraw()

    # 2. deposit and stake in new lp range
    prices = CoinGeckoAPI().get_price(
        ids=["badger-dao", "wrapped-bitcoin"], vs_currencies="usd"
    )
    wbtc_price = prices["wrapped-bitcoin"]["usd"]
    badger_price = prices["badger-dao"]["usd"]

    vault.init_bunni(r.bunni.badger_wbtc_bunni_token_309720_332580)
    amount0, amount1 = vault.bunni.get_amounts_for_liquidity(*vault.bunni.bunni_key)[1:]

    ratio = (amount1 / 1e18) / (amount0 / 1e8)
    amount0 = TREASURY_LIQ_TARGET / (wbtc_price + badger_price * ratio)
    amount0, amount1 = amount0 * 1e8, amount0 * ratio * 1e18

    badger.approve(vault.bunni.hub, 0)
    vault.bunni.deposit(amount0, amount1)
    vault.bunni.stake(r.bunni.badger_wbtc_bunni_gauge_309720_332580)

    vault.post_safe_tx()
