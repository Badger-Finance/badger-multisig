from helpers.addresses import r, reverse
from brownie import interface
from rich.console import Console
from rich.progress import track
import pandas as pd
from tabulate import tabulate
from brownie.exceptions import VirtualMachineError
from datetime import datetime

C = Console()

ACCOUNT = "0xB65cef03b9B89f99517643226d76e286ee999e77"

VAULTS = r.sett_vaults
STRATEGIES = {
    k: v for k, v in r.strategies.items() if k != "_deprecated"
}  # Filter out _deprecated group
CONTROLLERS = {
    k: v for k, v in r.controllers.items() if k != "dummy"
}  # Filter out dummy controller

PERMISSIONED_FUNCTIONS = [
    "governance",
    "strategist",
    "manager",
    "owner",
    "admin",
    "guardian",
]

INFRASTRUCTURE_TAGS = [
    "governance_timelock",
    "governance_timelock_veto",
    "rewardsLogger",
    "EmissionControl",
    "registry",
    "registry_v2",
    "registryAccessControl",
    "keeperAccessControl",
    "guardian",
    "GatedMiniMeController",
    "GlobalAccessControl",
    "harvest_forwarder",
    "badger_geyser",
    "slp_geyser",
    "aragon_voting",
    "badger_voting_shares",
    "brickedProxyAdmin",
    "brembadger",
    "digg_monetary_policy",
]

WALLETS_TAGS = [
    "badgertree",
    "native_autocompounder",
    "badgerhunt",
    "DAO_treasury",
    "rewards_escrow",
    "devProxyAdmin",
    "devUngatedProxyAdmin",
    "testProxyAdmin",
    "techOpsProxyAdmin",
    "opsProxyAdmin_old",
    "mStableSharedProxyAdmin",
    "rewardsEscrow",
    "gas_station",
    "upkeep_manager",
]


def main():
    check_permissions()


def check_permissions():
    # Combined data storage
    permissions_data = []

    # Check permissions for Vaults with progress bar
    C.print("[bold green]Processing Vaults...[/bold green]")
    for key, address in track(VAULTS.items(), description="Checking Vaults"):
        vault = interface.IInfraPermissions(address)
        permissions_data.extend(
            check_individual_permissions(key, address, "vault", vault)
        )

    # Check permissions for Strategies with progress bar
    C.print("[bold green]Processing Strategies...[/bold green]")
    for key, address in track(STRATEGIES.items(), description="Checking Strategies"):
        strategy = interface.IInfraPermissions(address)
        permissions_data.extend(
            check_individual_permissions(key, address, "strategy", strategy)
        )

    # Check permissions for Controllers with progress bar
    C.print("[bold green]Processing Controllers...[/bold green]")
    for key, address in track(CONTROLLERS.items(), description="Checking Controllers"):
        controller = interface.IInfraPermissions(address)
        permissions_data.extend(
            check_individual_permissions(key, address, "controller", controller)
        )

    # Check permissions for Infrastructure with progress bar
    C.print("[bold green]Processing Infrastructure...[/bold green]")
    for key in track(INFRASTRUCTURE_TAGS, description="Checking Infrastructure"):
        address = r[key]
        infra_contract = interface.IInfraPermissions(address)
        permissions_data.extend(
            check_individual_permissions(key, address, "infrastructure", infra_contract)
        )

    # # Check permissions for Wallets with progress bar
    C.print("[bold green]Processing Wallets...[/bold green]")
    for key in track(WALLETS_TAGS, description="Checking Wallets"):
        address = r.badger_wallets[key]
        wallet_contract = interface.IInfraPermissions(address)
        permissions_data.extend(
            check_individual_permissions(key, address, "wallet", wallet_contract)
        )

    # Convert to DataFrame
    permissions_df = pd.DataFrame(
        permissions_data,
        columns=[
            "Key",
            "Address",
            "Type",
            "Permission",
            "Actor",
            "Actor Name",
            "Matches ACCOUNT",
        ],
    )

    # Output the table
    merged_table = tabulate(
        permissions_df,
        headers=[
            "Key",
            "Address",
            "Type",
            "Permission",
            "Actor",
            "Actor Name",
            "Matches ACCOUNT",
        ],
        tablefmt="fancy_grid",
    )
    C.print(merged_table)

    # Generate the CSV file name
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"data/badger/governance_audit/governance_audit_{date_str}_{ACCOUNT}.csv"

    # Save DataFrame to CSV
    permissions_df.to_csv(filename, index=False)
    C.print(f"[bold green]CSV file saved as {filename}[/bold green]")


def check_individual_permissions(key, address, contract_type, contract):
    data = []

    for permission in PERMISSIONED_FUNCTIONS:
        try:
            func = getattr(contract, permission)
            actor = func()
            data.append(
                [
                    key,
                    address,
                    contract_type,
                    permission,
                    actor,
                    reverse[actor] if actor in reverse else "Unknown",
                    actor == ACCOUNT,
                ]
            )
        except (AttributeError, ValueError, VirtualMachineError):
            pass  # If the function does not exist or reverts, continue

    return data
