from great_ape_safe import GreatApeSafe
from helpers.addresses import r

from pycoingecko import CoinGeckoAPI


TARGET_VALUE = 500_000

prices = CoinGeckoAPI().get_price(
    ids=["badger-dao", "wrapped-bitcoin"], vs_currencies="usd"
)
wbtc_price = prices["wrapped-bitcoin"]["usd"]
badger_price = prices["badger-dao"]["usd"]


def recurse_deposit_amounts(amount0, amount1):
    # keep on adding to amounts (while maintaining appropriate token0/token1 ratio) until target is reached
    usd_value = (amount0 * wbtc_price) + (amount1 * badger_price)

    if usd_value > TARGET_VALUE:
        return amount0, amount1

    ratio = amount1 / amount0
    # add 0.05 wbtc and same ratio of badger each iteration
    amount0 = amount0 + 0.05
    amount1 = amount0 * ratio
    return recurse_deposit_amounts(amount0, amount1)


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_bunni(r.bunni.badger_wbtc_bunni_token)

    badger = vault.contract(r.treasury_tokens.BADGER)
    wbtc = vault.contract(r.treasury_tokens.WBTC)
    bunni_gauge = vault.contract(r.bunni.badger_wbtc_bunni_gauge)

    vault.take_snapshot(tokens=[badger, wbtc, bunni_gauge])

    amount0, amount1 = vault.bunni.get_amounts_for_liquidity(*vault.bunni.bunni_key)[1:]
    amount1_per_amount0 = (amount1 / 1e18) / (amount0 / 1e8)

    amount0, amount1 = recurse_deposit_amounts(1, amount1_per_amount0)

    vault.bunni.deposit(amount0 * 1e8, amount1 * 1e18)
    vault.bunni.stake(bunni_gauge.address)

    vault.post_safe_tx()
