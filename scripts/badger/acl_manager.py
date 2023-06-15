import os
from helpers.addresses import r
from great_ape_safe import GreatApeSafe
from rich.console import Console
from brownie import network, interface, web3
from helpers.constants import AddressZero
from tabulate import tabulate
import pandas as pd

C = Console()

ROLES_BY_KEY = {
    "badgerTree": [
        "DEFAULT_ADMIN_ROLE",
        "ROOT_PROPOSER_ROLE",
        "ROOT_VALIDATOR_ROLE",
        "PAUSER_ROLE",
        "UNPAUSER_ROLE",
    ],
    "rewardsLogger": ["DEFAULT_ADMIN_ROLE", "MANAGER_ROLE"],
    "guardian": ["DEFAULT_ADMIN_ROLE", "APPROVED_ACCOUNT_ROLE"],
    "keeper": ["DEFAULT_ADMIN_ROLE", "EARNER_ROLE", "HARVESTER_ROLE", "TENDER_ROLE"],
    "registryAccessControl": ["DEFAULT_ADMIN_ROLE", "DEVELOPER_ROLE"],
}
DEFAULT_ADMIN_ROLE = (
    "0x0000000000000000000000000000000000000000000000000000000000000000"
)

## Keeper ACL actions
def remove_from_keeper_acl(account):
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)
    keeper = safe.contract(r.keeperAccessControl)
    # Remove EARNER role
    ROLE = keeper.EARNER_ROLE()
    if keeper.hasRole(ROLE, account):
        keeper.revokeRole(ROLE, account)
        assert keeper.hasRole(ROLE, account) == False
        C.log(f"EARNER role removed for {account}")
    # Remove HARVESTER role
    ROLE = keeper.HARVESTER_ROLE()
    if keeper.hasRole(ROLE, account):
        keeper.revokeRole(ROLE, account)
        assert keeper.hasRole(ROLE, account) == False
        C.log(f"HARVESTER role removed for {account}")
    # Remove EARNER role
    ROLE = keeper.EARNER_ROLE()
    if keeper.hasRole(ROLE, account):
        keeper.revokeRole(ROLE, account)
        assert keeper.hasRole(ROLE, account) == False
        C.log(f"EARNER role removed for {account}")

    safe.post_safe_tx()


## Registry ACL actions
def remove_from_registry_acl(account):
    safe = GreatApeSafe(r.badger_wallets.techops_multisig)
    registry_acl = safe.contract(r.registryAccessControl)
    # Remove DEVELOPER role
    ROLE = registry_acl.DEVELOPER_ROLE()
    if registry_acl.hasRole(ROLE, account):
        registry_acl.revokeRole(ROLE, account)
        assert registry_acl.hasRole(ROLE, account) == False
        C.log(f"DEVELOPER role removed for {account}")

    safe.post_safe_tx()


## ACLs Auditor
def acl_audit(target_address=AddressZero):
    C.print("You are using the", network.show_active(), "network")
    registry = interface.IBadgerRegistryV2(r.registry_v2)

    total_data = []

    for key, roles in ROLES_BY_KEY.items():
        contract = registry.get(key)
        C.print(f"\n[blue]{key} - {contract}")
        if contract == AddressZero:
            C.print("[red]{key} not found on registry![/red]")
            continue
        accessControl = interface.IAccessControl(contract)

        contract_data = []

        for role in roles:
            hash = get_role_hash(role)
            role_member_count = accessControl.getRoleMemberCount(hash)
            for member_number in range(role_member_count):
                member_address = accessControl.getRoleMember(hash, member_number)
                contract_data.append(
                    {
                        "acl_contract": key,
                        "role": role,
                        "member_number": member_number,
                        "member_address": member_address,
                        "is_target": (target_address == member_address),
                    }
                )

        print(tabulate(contract_data, headers="keys", tablefmt="grid"))
        total_data += contract_data

    # build dataframe
    df = pd.DataFrame(total_data)
    # Dump result
    os.makedirs("data/badger/acl_roles_audit", exist_ok=True)
    df.to_csv(
        f"data/badger/acl_roles_audit/acl_roles_audit_{network.show_active()}.csv"
    )

    # Printout occurrences of target address
    if target_address != AddressZero:
        df_target = df[df["is_target"] == True]
        C.print(f"\n[blue]Target {target_address} has the following roles:")
        print(tabulate(df_target, headers="keys", tablefmt="grid"))
        # Dump result
        df_target.to_csv(
            f"data/badger/acl_roles_audit/acl_roles_audit_{network.show_active()}_{target_address}.csv"
        )


def get_role_hash(role):
    if role == "DEFAULT_ADMIN_ROLE":
        return DEFAULT_ADMIN_ROLE
    else:
        return web3.keccak(text=role).hex()
