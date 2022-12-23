from helpers.addresses import r
from great_ape_safe import GreatApeSafe
from rich.console import Console
from brownie import Contract

C = Console()

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