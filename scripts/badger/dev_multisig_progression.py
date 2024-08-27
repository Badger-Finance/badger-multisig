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
