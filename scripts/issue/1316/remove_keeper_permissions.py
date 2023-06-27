from helpers.addresses import r
from great_ape_safe import GreatApeSafe
from brownie import interface, web3
from tabulate import tabulate
from rich.console import Console

C = Console()

DEFAULT_ADMIN_ROLE = (
    "0x0000000000000000000000000000000000000000000000000000000000000000"
)
ROLES = ["DEFAULT_ADMIN_ROLE", "EARNER_ROLE", "HARVESTER_ROLE", "TENDER_ROLE"]

BOT_SQUAD = r.badger_wallets.ops_botsquad

def main():
    dev = GreatApeSafe(r.badger_wallets.dev_multisig)
    keeper_acl = interface.IAccessControl(r.keeperAccessControl, owner=dev.account)

    # Check all active accounts per role and remove if not bot
    contract_data = []
    for role in ROLES:
        hash = get_role_hash(role)
        role_member_count = keeper_acl.getRoleMemberCount(hash)
        for member_number in range(role_member_count):
            member_address = keeper_acl.getRoleMember(hash, member_number)
            contract_data.append(
                {
                    "role": role,
                    "member_number": member_number,
                    "member_address": member_address
                }
            )
            if member_address != BOT_SQUAD and hash != DEFAULT_ADMIN_ROLE:
                keeper_acl.revokeRole(hash, member_address)
                C.print(f"[green]Revoking {role} from {member_address}[/green]")

    C.print("\nInitial State:\n")
    print(tabulate(contract_data, headers="keys", tablefmt="grid"))

    # Get and print final state
    contract_data = []
    for role in ROLES:
        hash = get_role_hash(role)
        role_member_count = keeper_acl.getRoleMemberCount(hash)
        for member_number in range(role_member_count):
            member_address = keeper_acl.getRoleMember(hash, member_number)
            contract_data.append(
                {
                    "role": role,
                    "member_number": member_number,
                    "member_address": member_address
                }
            )

    C.print("\nInitial State:\n")
    print(tabulate(contract_data, headers="keys", tablefmt="grid"))

    
def get_role_hash(role):
    if role == "DEFAULT_ADMIN_ROLE":
        return DEFAULT_ADMIN_ROLE
    else:
        return web3.keccak(text=role).hex()