from great_ape_safe import GreatApeSafe
from helpers.addresses import r

from pycoingecko import CoinGeckoAPI


BADGER_USD = 250_000


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_bunni(r.bunni.badger_wbtc_bunni_token)

    badger = vault.contract(r.treasury_tokens.BADGER)
    wbtc = vault.contract(r.treasury_tokens.WBTC)
    bunni_gauge = vault.contract(r.bunni.badger_wbtc_bunni_gauge)

    vault.take_snapshot(tokens=[badger, wbtc, bunni_gauge])

    prices = CoinGeckoAPI().get_price("badger-dao", "usd")
    badger_price = prices["badger-dao"]["usd"]

    amount_badger = (BADGER_USD / badger_price) * 1e18
    amount_wbtc = vault.bunni.get_amount_out([badger, wbtc], amount_badger)

    vault.bunni.deposit(amount_wbtc, amount_badger)
    vault.bunni.stake(bunni_gauge.address)

    vault.post_safe_tx()
