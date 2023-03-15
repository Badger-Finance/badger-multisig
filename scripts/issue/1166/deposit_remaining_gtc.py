from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# https://app.uniswap.org/#/pool/435187
TOKEN_ID = 435187


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_uni_v3()

    gtc = vault.contract(r.treasury_tokens.GTC)
    weth = vault.contract(r.treasury_tokens.WETH)

    vault.take_snapshot(tokens=[gtc])

    vault.uni_v3.increase_liquidity(TOKEN_ID, weth, gtc, 0, gtc.balanceOf(vault))

    vault.post_safe_tx()
