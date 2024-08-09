from helpers.addresses import r, reverse
from brownie import web3
from rich.console import Console
from rich.progress import track
import pandas as pd
from tabulate import tabulate
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
    check_upgradeability()


def check_upgradeability():
    # Combined data storage
    upgradeability_data = []

    # Check upgradeability for Vaults with progress bar
    C.print("[bold green]Checking Upgradeability for Vaults...[/bold green]")
    for key, address in track(VAULTS.items(), description="Checking Vaults"):
        upgradeability_data.append(
            check_admin_upgradeability(key, address, "vault")
        )

    # Check upgradeability for Strategies with progress bar
    C.print("[bold green]Checking Upgradeability for Strategies...[/bold green]")
    for key, address in track(STRATEGIES.items(), description="Checking Strategies"):
        upgradeability_data.append(
            check_admin_upgradeability(key, address, "strategy")
        )

    # Check upgradeability for Controllers with progress bar
    C.print("[bold green]Checking Upgradeability for Controllers...[/bold green]")
    for key, address in track(CONTROLLERS.items(), description="Checking Controllers"):
        upgradeability_data.append(
            check_admin_upgradeability(key, address, "controller")
        )

    # Check upgradeability for Infrastructure with progress bar
    C.print("[bold green]Checking Upgradeability for Infrastructure...[/bold green]")
    for key in track(INFRASTRUCTURE_TAGS, description="Checking Infrastructure"):
        address = r[key]
        upgradeability_data.append(
            check_admin_upgradeability(key, address, "infrastructure")
        )

    # Check upgradeability for Wallets with progress bar
    C.print("[bold green]Checking Upgradeability for Wallets...[/bold green]")
    for key in track(WALLETS_TAGS, description="Checking Wallets"):
        address = r.badger_wallets[key]
        upgradeability_data.append(
            check_admin_upgradeability(key, address, "wallet")
        )

    # Convert to DataFrame
    upgradeability_df = pd.DataFrame(
        upgradeability_data,
        columns=[
            "Key",
            "Address",
            "Type",
            "Admin",
            "Admin Name",
            "Matches ACCOUNT",
        ],
    )

    # Tabulate and print the results
    merged_table = tabulate(
        upgradeability_df,
        headers=[
            "Key",
            "Address",
            "Type",
            "Admin",
            "Admin Name",
            "Matches ACCOUNT",
        ],
        tablefmt="fancy_grid",
    )
    C.print(merged_table)

    # Generate the CSV file name
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"data/badger/governance_audit/upgradeablilty_audit_{date_str}_{ACCOUNT}.csv"

    # Save DataFrame to CSV
    upgradeability_df.to_csv(filename, index=False)
    C.print(f"[bold green]CSV file saved as {filename}[/bold green]")


def check_admin_upgradeability(key, address, contract_type):
    try:
        admin_storage_slot = web3.eth.getStorageAt(
            address, "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"
        ).hex()

        if admin_storage_slot in [
            "0x0000000000000000000000000000000000000000000000000000000000000000",
            "0x0x"
        ]:
            admin = "Not a proxy"
        else:
            admin = web3.toChecksumAddress(f"0x{admin_storage_slot[-40:]}")  # Extract admin address
    except ValueError:
        admin = "Not a proxy"

    return [
        key,
        address,
        contract_type,
        admin,
        reverse[admin] if admin in reverse else "Unknown",
        admin == ACCOUNT,
    ]


if __name__ == "__main__":
    main()
