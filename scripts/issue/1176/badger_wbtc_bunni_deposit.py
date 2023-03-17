from great_ape_safe import GreatApeSafe
from helpers.addresses import r

from pycoingecko import CoinGeckoAPI


prices = CoinGeckoAPI().get_price(
    ids=["badger-dao", "wrapped-bitcoin"], vs_currencies="usd"
)
wbtc_price = prices["wrapped-bitcoin"]["usd"]
badger_price = prices["badger-dao"]["usd"]


def main(target_value=500_000):
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_bunni(r.bunni.badger_wbtc_bunni_token)

    badger = vault.contract(r.treasury_tokens.BADGER)
    wbtc = vault.contract(r.treasury_tokens.WBTC)
    bunni_gauge = vault.contract(r.bunni.badger_wbtc_bunni_gauge)

    vault.take_snapshot(tokens=[badger, wbtc, bunni_gauge])

    amount0, amount1 = vault.bunni.get_amounts_for_liquidity(*vault.bunni.bunni_key)[1:]

    ratio = (amount1 / 1e18) / (amount0 / 1e8)
    amount0 = target_value / (wbtc_price + badger_price * ratio)
    amount0, amount1 = amount0 * 1e8, amount0 * ratio * 1e18

    vault.bunni.deposit(amount0, amount1)
    vault.bunni.stake(bunni_gauge.address)

    vault.post_safe_tx()
