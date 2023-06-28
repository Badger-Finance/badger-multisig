from helpers.addresses import r
from great_ape_safe import GreatApeSafe
from brownie import interface, web3
from tabulate import tabulate
from rich.console import Console

C = Console()

DEFAULT_ADMIN_ROLE = (
    "0x0000000000000000000000000000000000000000000000000000000000000000"
)
KEEPER_ROLES = ["EARNER_ROLE", "HARVESTER_ROLE", "TENDER_ROLE"]
REGISTRY_ROLES = ["DEVELOPER_ROLE"]

BOT_SQUAD = r.badger_wallets.ops_botsquad


def remove_keeper_acl_roles():
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)
    keeper_acl = interface.IAccessControl(r.keeperAccessControl, owner=safe.account)

    # Check all active accounts per role
    data = get_and_print_acl_roles_members(keeper_acl, KEEPER_ROLES)

    # Remove all roles members from KeeperACL (Except harvester on bot and ADMIN)
    for role in KEEPER_ROLES:
        hash = get_role_hash(role)
        for member_address in get_member_addresses_by_role(data, role):
            if not (role == "HARVESTER_ROLE" and member_address == BOT_SQUAD):
                keeper_acl.revokeRole(hash, member_address)
                C.print(f"[green]Revoking {role} from {member_address}[/green]")

    # Get and print final state
    get_and_print_acl_roles_members(keeper_acl, KEEPER_ROLES)

    safe.post_safe_tx()


def remove_registry_acl_roles():
    safe = GreatApeSafe(r.badger_wallets.techops_multisig)
    registry_acl = interface.IAccessControl(r.registryAccessControl, owner=safe.account)

    # Check all active accounts per role and remove if not bot
    data = get_and_print_acl_roles_members(registry_acl, REGISTRY_ROLES)

    # Remove all roles' memebers
    for role in REGISTRY_ROLES:
        hash = get_role_hash(role)
        for member_address in get_member_addresses_by_role(data, role):
            registry_acl.revokeRole(hash, member_address)
            C.print(f"[green]Revoking {role} from {member_address}[/green]")

    # Get and print final state
    get_and_print_acl_roles_members(registry_acl, REGISTRY_ROLES)

    safe.post_safe_tx()


def get_role_hash(role):
    if role == "DEFAULT_ADMIN_ROLE":
        return DEFAULT_ADMIN_ROLE
    else:
        return web3.keccak(text=role).hex()


def get_and_print_acl_roles_members(acl_contract, roles):
    contract_data = []
    for role in roles:
        hash = get_role_hash(role)
        role_member_count = acl_contract.getRoleMemberCount(hash)
        for member_number in range(role_member_count):
            member_address = acl_contract.getRoleMember(hash, member_number)
            contract_data.append(
                {
                    "role": role,
                    "member_number": member_number,
                    "member_address": member_address,
                }
            )
    C.print("[blue]\nRoles State:\n[/blue]")
    print(tabulate(contract_data, headers="keys", tablefmt="grid"))
    return contract_data


def get_member_addresses_by_role(contract_data, role):
    member_addresses = []
    for entry in contract_data:
        if entry["role"] == role:
            member_addresses.append(entry["member_address"])
    return member_addresses
