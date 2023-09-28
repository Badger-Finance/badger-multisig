from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# flag
prod = False

# slippage
COEF = 0.98

# bit extra compare in case we fall short with some other orders + orders fee when deducted
# ref: https://docs.google.com/spreadsheets/d/1g0khFgtGOuhooMMxmBHbmFPFje4TrLDzDV-WRBrmtQQ/edit#gid=0
DAI_TO_SELL = 80_000 * 1e18


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_cow(prod)

    # tokens
    dai = vault.contract(r.treasury_tokens.DAI)
    usdc = vault.contract(r.treasury_tokens.USDC)

    vault.cow.market_sell(dai, usdc, DAI_TO_SELL, deadline=60 * 60 * 24, coef=COEF)

    vault.post_safe_tx()
