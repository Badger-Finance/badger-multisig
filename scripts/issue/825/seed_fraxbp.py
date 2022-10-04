from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from pycoingecko import CoinGeckoAPI


cg = CoinGeckoAPI()

AMOUNT_USDC = 250_000


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_curve()

    badger = vault.contract(r.treasury_tokens.BADGER)
    usdc = vault.contract(r.treasury_tokens.USDC)
    frax = vault.contract(r.treasury_tokens.FRAX)

    pool = vault.contract(r.crv_factory_pools.badgerFRAXBP_f)
    lp = vault.contract(r.treasury_tokens.badgerFRAXBP_f_lp)
    fraxbp_zap = vault.contract(r.curve.zap_fraxbp)

    vault.take_snapshot(tokens=[badger, usdc, lp.address])

    badger_rate = (
        cg.get_price(ids="badger-dao", vs_currencies="usd")["badger-dao"]["usd"]
    )

    amount_badger = (AMOUNT_USDC / badger_rate) * 1e18
    amount_usdc = AMOUNT_USDC * 1e6

    vault.curve.deposit_zapper(
        fraxbp_zap, pool, [badger, frax, usdc], [amount_badger, 0, amount_usdc], seeding=True
    )

    vault.print_snapshot()
    vault.post_safe_tx()
