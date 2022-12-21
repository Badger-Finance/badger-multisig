from rich.console import Console
from brownie import interface
from helpers.addresses import r

console = Console()

SIGNER = ""

def main():
    msigs = r.badger_wallets

    for key, addr in msigs.items():
        try:
            safe = interface.IGnosisSafe_v1_3_0(addr)
            owners = safe.getOwners()
            if SIGNER in owners:
                console.print(f"[green]Signer found on {key}: {addr}[/green]")
        except:
            console.print(f"[red]{key} is not a safe[/red]")
