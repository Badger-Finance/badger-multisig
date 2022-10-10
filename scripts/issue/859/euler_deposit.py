from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import interface
from rich.console import Console

console = Console()


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_euler()
    
    badger = vault.contract(r.treasury_tokens.BADGER)
    ebadger = interface.IEToken(
            vault.euler.markets.underlyingToEToken(badger)
        )

    vault.take_snapshot(tokens=[badger, ebadger])

    vault.euler.deposit(badger, 100_000e18)

    vault.print_snapshot()
    vault.post_safe_tx()
