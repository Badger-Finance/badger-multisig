from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console

console = Console()

prod = False

def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_cow(prod=prod)

    wbtc = vault.contract(r.treasury_tokens.WBTC)
    weth = vault.contract(r.treasury_tokens.WETH)

    vault.cow.market_sell(wbtc, weth, 30e8, deadline=60 * 60 * 4)
    vault.post_safe_tx()