from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import interface
from rich.console import Console

console = Console()


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_euler()
    
    badger = vault.contract(r.treasury_tokens.BADGER)
    ebadger = interface.IERC20(
            vault.euler.markets.underlyingToEToken(badger)
        )

    before_ebadger = ebadger.balanceOf(vault) / 1e18

    vault.take_snapshot(tokens=[badger])

    vault.euler.deposit(badger, 250_000e18)

    after_ebadger = ebadger.balanceOf(vault)/ 1e18
    delta = after_ebadger - before_ebadger

    console.print(f"{before_ebadger=}")
    console.print(f"{after_ebadger=}")
    console.print(f"{delta=}")

    vault.print_snapshot()
    vault.post_safe_tx()