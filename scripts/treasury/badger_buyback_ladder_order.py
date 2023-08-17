from decimal import Decimal
from math import log, floor
from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from great_ape_safe.ape_api.helpers.coingecko import get_cg_price


SAFE = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
USDT = SAFE.contract(r.treasury_tokens.USDT)
BADGER = SAFE.contract(r.treasury_tokens.BADGER)

COW_PROD = True

MAX_USDT = 500_000
MAX_BADGER = 200_000
LEG_AMOUNT = 100_000
DEADLINE = 60 * 60 * 24 * 7  # gives one week to sell
DECIMALS = USDT.decimals()


def main(usdt_remaining=(MAX_USDT * 0.7), badger_bought=64151.1085, approve=True):
    usdt_remaining_int = int(usdt_remaining)
    SAFE.init_cow(prod=COW_PROD)
    if approve:
        amount_to_approve = (
            int(usdt_remaining_int / LEG_AMOUNT) * LEG_AMOUNT * 10 ** DECIMALS
        )
        SAFE.cow.allow_relayer(USDT, amount_to_approve)

    cg_price = get_cg_price(BADGER.address)
    total_badger = float(badger_bought)
    for i in range(int(usdt_remaining_int / LEG_AMOUNT)):
        coefficient = 1.05 + (i * 0.025)
        total_badger = total_badger + (
            LEG_AMOUNT / (cg_price / coefficient)
        )  # Rough estimate, does not take fees into account
        if total_badger < MAX_BADGER:
            SAFE.cow.market_sell(
                asset_sell=USDT,
                asset_buy=BADGER,
                mantissa_sell=LEG_AMOUNT * 10 ** DECIMALS,
                deadline=DEADLINE,
                coef=coefficient,
                destination=r.badger_wallets.treasury_vault_multisig,
            )
        else:
            print("Buy amount would exceed buyback total!")

    SAFE.post_safe_tx()
