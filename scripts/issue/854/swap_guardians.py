from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console

C = Console()

ACCOUNTS_TO_REMOVE = [
    "ops_executor1",
    "ops_deployer2",
    "ops_executor4",
    "ops_deployer5"
]

ACCOUNTS_TO_ADD = [
    "ops_deployer6",
    "ops_executor4",
    "ops_deployer2",
]

DEPRECATED_OPS_WALLETS = r.badger_wallets._deprecated
ACTIVE_OPS_WALLETS = r.badger_wallets

def main():
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)
    guardian = safe.contract(r.guardian)

    role = guardian.APPROVED_ACCOUNT_ROLE()

    # Remove roles
    for account in ACCOUNTS_TO_REMOVE:
        address = DEPRECATED_OPS_WALLETS[account]
        C.print(f"[red]Revoking role from {account}: {address}[/red]")
        guardian.revokeRole(role, address)
        assert guardian.hasRole(role, address) == False

    # Grant roles
    for account in ACCOUNTS_TO_ADD:
        address = ACTIVE_OPS_WALLETS[account]
        C.print(f"[green]Granting role to {account}: {address}[/green]")
        guardian.grantRole(role, address)
        assert guardian.hasRole(role, address)

    safe.post_safe_tx()
