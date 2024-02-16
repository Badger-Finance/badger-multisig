from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# slippages
COEF = 0.95
DEADLINE = 60 * 60 * 12


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_liquis()
    vault.init_cow(prod=True)

    # bunni lp
    bunni_lp = vault.contract(r.bunni.badger_wbtc_bunni_token_309720_332580)

    # tokens
    liq = vault.contract(r.treasury_tokens.LIQ)
    weth = vault.contract(r.treasury_tokens.WETH)
    olit = vault.contract(r.bunni.oLIT)

    vault.take_snapshot(tokens=[liq, olit, bunni_lp])

    vault.liquis.unstake_all_and_withdraw_all(bunni_lp)

    # gov tokens graceful exit
    # liquidity situation overview: https://info.uniswap.org/#/tokens/0xd82fd4d6d62f89a1e50b1db69ad19932314aa408
    vault.cow.market_sell(liq, weth, liq.balanceOf(vault), deadline=DEADLINE, coef=COEF)

    vault.post_safe_tx()
