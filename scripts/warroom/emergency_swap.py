from rich.console import Console
from decimal import Decimal

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

console = Console()

prod = False


def main(symbol_in, symbol_out, amount=None, use_3pool="true"):
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)

    tokens = {
        "usdc": vault.contract(r.treasury_tokens.USDC),
        "usdt": vault.contract(r.treasury_tokens.USDT),
        "dai": vault.contract(r.treasury_tokens.DAI),
    }

    token_in = tokens[symbol_in]
    token_out = tokens[symbol_out]
    amount = token_in.balanceOf(vault) if not amount else int(amount) * 10 ** token_in.decimals()

    vault.take_snapshot(tokens=[token_in, token_out])

    if use_3pool == "true":
        vault.init_curve()
        vault.curve.swap(token_in, token_out, amount)

    else:
        vault.init_cow(prod=prod)
        vault.cow.market_sell(token_in, token_out, amount, 60 * 60 * 4)

    vault.print_snapshot()
    vault.post_safe_tx()
