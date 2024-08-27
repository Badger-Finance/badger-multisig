from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import interface
from rich.console import Console

C = Console()

"""
The following set of scripts are meant to perform key actions to progress the Dev Multisig 
into a more decentralized state. These actions were defined based on the observations obtained from the
governance and upgradeability access audit.
"""

# Actors involved
DEV = r.badger_wallets.dev_multisig
TECHOPS = r.badger_wallets.techops_multisig
TREASURY = r.badger_wallets.treasury_vault_multisig
COMMUNITY = r.badger_wallets.community_council_multisig
BACKUP = r.badger_wallets.dev_multisig_backup

# Contracts involved
ACL = [
    r.GlobalAccessControl,
    r.guardian,
    r.keeperAccessControl,
    r.rewardsLogger,
    r.badger_wallets.badgertree,
]

TIMELOCK = r.governance_timelock

# Controllers and vaults not governed by the Timelock
CONTROLLERS = [
    "bbveCVX-CVX-f",
    "ibBTCCrv",
    "restitution",
    "bcrvBadger",
]
VAULTS = [
    "bcrvRenBTC",
    "bcrvIbBTC",
    "bcvxCRV",
    "bveCVX",
    "bbveCVX_CVX_f",
    "remBADGER",
    "remDIGG",
    "bcrvBadger",
    "graviAURA",
    "bauraBal",
    "b80BADGER_20WBTC",
    "b40WBTC_40DIGG_20graviAURA",
    "bBB_a_USD",
    "b33auraBAL_33graviAURA_33WETH",
    "bB_stETH_STABLE",
    "bB_rETH_STABLE",
]

# Constants
DEFAULT_ADMIN_ROLE = (
    "0x0000000000000000000000000000000000000000000000000000000000000000"
)
SENTINEL_OWNERS = "0x0000000000000000000000000000000000000001"

FINAL_DEV_MULTISG_STATE = [
    TREASURY,
    TECHOPS,
    COMMUNITY,
    BACKUP,
]

FINAL_POLICY = 3


def step_1_1():
    """
    - Transfer the DEFAULT_ADMIN_ROLE for GlobalAccessControl, Guardian, KeeperACL, RewardsLogger,
      and BadgerTree from the Dev Multisig to the Badger TechOps multisig.
    """

    dev = GreatApeSafe(DEV)

    for acl_address in ACL:
        acl = dev.contract(acl_address, Interface=interface.IAccessControl)
        # Confirm that the Dev multisig holds the DEFAULT_ADMIN_ROLE (and nobody else does)
        assert acl.getRoleMemberCount(DEFAULT_ADMIN_ROLE) == 1
        assert acl.hasRole(DEFAULT_ADMIN_ROLE, DEV)
        # Grant role to TechOps (Dev multisig keeps it to simplify things)
        C.print(f"Granting admin role to TechOps on {acl_address}")
        acl.grantRole(DEFAULT_ADMIN_ROLE, TECHOPS)
        assert acl.getRoleMemberCount(DEFAULT_ADMIN_ROLE) == 2
        assert acl.hasRole(DEFAULT_ADMIN_ROLE, TECHOPS)

    dev.post_safe_tx()


def step_1_2():
    """
    - Transfer governance of the remaining vaults and controllers, including remBADGER, from the Dev Multisig to
      the Governance Timelock (for vaults not already governed by the Timelock).
    """

    dev = GreatApeSafe(DEV)

    # Confirm governance is held by the Dev Multisig and transfer it to the Timelock for each of the vaults
    for vault_ID in VAULTS:
        vault = dev.contract(r.sett_vaults[vault_ID], interface.ISettV4h)
        assert vault.governance() == DEV
        C.print(f"Transfering governance to Timelock on vault: {vault_ID}")
        vault.setGovernance(TIMELOCK)
        assert vault.governance() == TIMELOCK

    # Confirm governance is held by the Dev Multisig and transfer it to the Timelock for each of the controllers
    for controller_ID in CONTROLLERS:
        controller = dev.contract(r.controllers[controller_ID], interface.IController)
        assert controller.governance() == DEV
        C.print(f"Transfering governance to Timelock on controller: {controller_ID}")
        controller.setGovernance(TIMELOCK)
        assert controller.governance() == TIMELOCK

    dev.post_safe_tx()


def step_2():
    """
    Replace Dev Multisig signers with the following multisigs and change its policy to 3/4:
        - Treasury Vault
        - Badger TechOps
        - Community Council
        - Security Backup (Third party security partner)
    """

    dev = GreatApeSafe(DEV)
    dev_multisig = interface.IGnosisSafe_v1_3_0(DEV, owner=dev.account)

    dev_current = dev_multisig.getOwners()

    unique_to_current = list(set(dev_current).difference(set(FINAL_DEV_MULTISG_STATE)))
    unique_to_final = list(set(FINAL_DEV_MULTISG_STATE).difference(set(dev_current)))

    # Swap out any unique addresses to the Dev Multisig
    for i in range(len(unique_to_final)):
        C.print(f"Swapping {unique_to_current[i]} for {unique_to_final[i]}...")

        dev_multisig.swapOwner(
            get_previous_owner(dev_multisig, unique_to_current[i]),
            unique_to_current[i],
            unique_to_final[i],
        )

    # Remove any outstanding owners
    dev_current = dev_multisig.getOwners()
    for owner in dev_current:
        if owner not in FINAL_DEV_MULTISG_STATE:
            C.print(f"Removing {owner}...")
            dev_multisig.removeOwner(
                get_previous_owner(dev_multisig, owner), owner, FINAL_POLICY
            )

    # Confirm all owners
    for owner in dev_multisig.getOwners():
        assert owner in FINAL_DEV_MULTISG_STATE
    assert len(dev_multisig.getOwners()) == len(FINAL_DEV_MULTISG_STATE)
    assert dev_multisig.getThreshold() == FINAL_POLICY

    C.print(f"\nNew Owners at dev_multisig Multisig:")
    C.print(f"[green]{dev_multisig.getOwners()}[/green]\n")
    C.print(f"[green]{dev_multisig.getThreshold()}[/green]\n")

    dev.post_safe_tx()


def get_previous_owner(dev, owner):
    owners = dev.getOwners()
    for i in range(len(owners)):
        if owners[i] == owner:
            if i == 0:
                return SENTINEL_OWNERS
            else:
                return owners[i - 1]
