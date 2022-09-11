"""
Note
----
Po — 09/20/2021
better to use 10% / 365 * 7
So 10 M TVL, 10% = 1M in Badger emitted over the year / 365 * 7 = 19,178 USD needs to be emitted next week, 
Badger price is at $19.178, so we need to emit 1000 Badger
"""

from brownie import Contract
from pycoingecko import CoinGeckoAPI
from helpers.addresses import registry
import numpy as np

COINGECKO_IDS = {"BADGER": "badger-dao", "CVX": "convex-finance"}


def dynamic_bveCVX_emissions():
    cg = CoinGeckoAPI()
    bveCVX = Contract(registry.eth.sett_vaults.bveCVX)

    decimals = bveCVX.decimals()
    total_supply = bveCVX.totalSupply()
    ppfs = bveCVX.getPricePerFullShare() / 10**decimals

    total_cvx_aum = total_supply * ppfs

    spot_prices = cg.get_price(
        ids=[COINGECKO_IDS["BADGER"], COINGECKO_IDS["CVX"]], vs_currencies="usd"
    )
    spot_price_badger = spot_prices[COINGECKO_IDS["BADGER"]]["usd"]
    spot_price_cvx = spot_prices[COINGECKO_IDS["CVX"]]["usd"]

    # historical prices of CVX
    history_arr_cvx = cg.get_coin_market_chart_by_id(
        id=COINGECKO_IDS["CVX"], vs_currency="usd", days=91, interval="daily"
    )["prices"]
    history_prices_cvx = [x[1] for x in history_arr_cvx]
    cvx_price_7d_avg = np.average(history_prices_cvx[-7:])

    # historical prices of BADGER
    history_arr_badger = cg.get_coin_market_chart_by_id(
        id=COINGECKO_IDS["BADGER"], vs_currency="usd", days=91, interval="daily"
    )["prices"]
    history_prices_badger = [x[1] for x in history_arr_badger]
    badger_price_7d_avg = np.average(history_prices_badger[-7:])

    # use 7d average vs spot price
    badger_rate = min(spot_price_badger, badger_price_7d_avg)
    cvx_rate = min(spot_price_cvx, cvx_price_7d_avg)

    print(f"badger_rate={badger_rate}")
    print(f"cvx_rate={cvx_rate}")

    cvx_aum_formatted = total_cvx_aum / 10**decimals

    print(f"\n ==== cvx_aum_usd={cvx_aum_formatted * spot_price_cvx} ==== ")

    badger_usd_value_to_emit = ((cvx_aum_formatted * cvx_rate * 0.15) / 365) * 7

    print(f" ==== badger_usd_value_to_emit={badger_usd_value_to_emit} ==== ")

    badger_units = badger_usd_value_to_emit / badger_rate

    print(f" ==== badger_units={badger_units} ==== \n")

    # badger has same decimals as CVX, reuse
    return badger_units * 10**decimals
