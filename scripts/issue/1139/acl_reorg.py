from brownie import accounts, chain, Contract, interface, multicall, web3

from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console

C = Console()

dev_msig = GreatApeSafe(r.badger_wallets.dev_multisig)
techops = GreatApeSafe(r.badger_wallets.techops_multisig)

# General role
DEFAULT_ADMIN_ROLE = (
    "0x0000000000000000000000000000000000000000000000000000000000000000"
)
# BadgerTree
PAUSER_ROLE = web3.solidityKeccak(["string"], ["PAUSER_ROLE"]).hex()
UNPAUSER_ROLE = web3.solidityKeccak(["string"], ["UNPAUSER_ROLE"]).hex()
ROOT_PROPOSER_ROLE = web3.solidityKeccak(["string"], ["ROOT_PROPOSER_ROLE"]).hex()
ROOT_VALIDATOR_ROLE = web3.solidityKeccak(["string"], ["ROOT_VALIDATOR_ROLE"]).hex()
# Rewards Logger
MANAGER_ROLE = web3.solidityKeccak(["string"], ["MANAGER_ROLE"]).hex()
# Guardian
APPROVED_ACCOUNT_ROLE = web3.solidityKeccak(["string"], ["APPROVED_ACCOUNT_ROLE"]).hex()
# Keeper ACL
EARNER_ROLE = web3.solidityKeccak(["string"], ["EARNER_ROLE"]).hex()
HARVESTER_ROLE = web3.solidityKeccak(["string"], ["HARVESTER_ROLE"]).hex()
TENDER_ROLE = web3.solidityKeccak(["string"], ["TENDER_ROLE"]).hex()
# registryAccessControl
DEVELOPER_ROLE = web3.solidityKeccak(["string"], ["DEVELOPER_ROLE"]).hex()

# techops signers
techops_signers = list(
    interface.IGnosisSafe_v1_3_0(r.badger_wallets.techops_multisig).getOwners()
)
# print them in terminal for visibilitys
C.print(techops_signers)

GUARDIAN_BACKUPS = [
    r.badger_wallets.guardian_backups.ops_executor7,
    r.badger_wallets.guardian_backups.defender1,
    r.badger_wallets.guardian_backups.defender2,
]
DEVELOPER_ROLE_MEMBERS = list(techops_signers + GUARDIAN_BACKUPS)

# https://github.com/Badger-Finance/badger-multisig/issues/1139#issue-1584654926
TARGET_CONFIG_DEV_MSIG = {
    "badgerTree": {
        DEFAULT_ADMIN_ROLE: r.badger_wallets.dev_multisig,
        PAUSER_ROLE: r.guardian,
        UNPAUSER_ROLE: r.badger_wallets.dev_multisig,
        ROOT_PROPOSER_ROLE: r.badger_wallets.ops_botsquad_cycle0,
        ROOT_VALIDATOR_ROLE: r.badger_wallets["ops_root-validator_v3"],
    },
    "rewardsLogger": {
        DEFAULT_ADMIN_ROLE: r.badger_wallets.dev_multisig,
        MANAGER_ROLE: r.badger_wallets.techops_multisig,
    },
    "guardian": {
        DEFAULT_ADMIN_ROLE: r.badger_wallets.dev_multisig,
        APPROVED_ACCOUNT_ROLE: DEVELOPER_ROLE_MEMBERS,
    },
    "keeperAccessControl": {
        DEFAULT_ADMIN_ROLE: r.badger_wallets.dev_multisig,
        EARNER_ROLE: techops_signers,
        HARVESTER_ROLE: techops_signers,
        TENDER_ROLE: techops_signers,
    },
}

TARGET_CONFIG_TECHOPS = {
    "registryAccessControl": {
        DEFAULT_ADMIN_ROLE: r.badger_wallets.techops_multisig,
        DEVELOPER_ROLE: techops_signers,
    },
}


def sim():
    chain_id = chain.id
    if chain_id == 1:
        # 1. ops_multisig_old -> grant role `ADMIN_ROLE` in rewardsLogger to dev_multisig
        ops_multisig_granting(sim=True)
    elif chain_id == 42161:
        # 1. dev_multisig_deprecated -> grant role `ADMIN_ROLE` in guardian to dev_multisig
        deprecated_dev_granting(sim=True)
    # 2. sim atomic tx
    main("dev.badgerdao.eth", sim=True)


def ops_multisig_granting(sim=False):
    ops_multisig_old = GreatApeSafe(r.badger_wallets.ops_multisig_old)

    reward_logger = ops_multisig_old.contract(r.rewardsLogger)
    reward_logger.grantRole(DEFAULT_ADMIN_ROLE, dev_msig)

    if not sim:
        ops_multisig_old.post_safe_tx(call_trace=True)


# NOTE: replace your address here with rights to post tx into dev_multisig_deprecated
ACCOUNT_NAME = ""


def deprecated_dev_granting(sim=False):
    if sim:
        dev = accounts.at(r.badger_wallets.ops_deployer4, force=True)
    else:
        dev = accounts.load(ACCOUNT_NAME)

    safe = interface.IMultisigWalletWithDailyLimit(
        r.badger_wallets.dev_multisig_deprecated
    )

    registry = Contract(r.registry_v2)
    guardian = Contract(registry.get("guardian"))

    calldata_grant_role = guardian.grantRole.encode_input(DEFAULT_ADMIN_ROLE, dev_msig)

    safe.submitTransaction(guardian, 0, calldata_grant_role, {"from": dev})

    if sim:
        owners = safe.getOwners()[0:2]
        for owner in owners:
            signer = accounts.at(owner, force=True)
            safe.confirmTransaction(safe.transactionCount() - 1, {"from": signer})

    C.print(
        f"Calldata for granting ADMIN_ROLE to dev_msig=[blue]{calldata_grant_role}[/blue]. Target:[blue]{guardian.address}[/blue]\n"
    )


def main(safe_ens, sim=False):
    # NOTE: before heading towards configuration, ensure current techops signers are in gas st for `MAINNET`
    if chain.id == 1:
        # watchlist in gas st
        gas_st_watchlist = Contract(r.badger_wallets.gas_station).getWatchList()
        for signer in techops_signers:
            assert signer is gas_st_watchlist, f"Signer {signer} not in watchlist!"

    target_config, safe = (
        (TARGET_CONFIG_DEV_MSIG, dev_msig)
        if "dev.badgerdao.eth" == safe_ens
        else (TARGET_CONFIG_TECHOPS, techops)
    )

    registry = safe.contract(r.registry_v2, Interface=interface.IBadgerRegistryV2)

    for contract_name in target_config:
        target = safe.contract(registry.get(contract_name), from_explorer=True)
        C.print(f"Processing configuration for {contract_name} at {target}\n")

        roles_targets = target_config[contract_name]

        for role in roles_targets:
            expected_addrs_per_setting = target_config[contract_name][role]

            if not isinstance(expected_addrs_per_setting, str):
                count = target.getRoleMemberCount(role)
                with multicall:
                    members = [target.getRoleMember(role, i) for i in range(count)]

                for addr in expected_addrs_per_setting:
                    if not target.hasRole(role, addr):
                        C.print(f"Grant role {role} in {contract_name} for {addr}\n")
                        target.grantRole(role, addr)

                C.print(
                    f"Role {role} in {contract_name} has {count} members, checking against target config...\n"
                )
                for member in members:
                    if not member is expected_addrs_per_setting:
                        C.print(f"Revoke role {role} in {contract_name} for {member}\n")
                        target.revokeRole(role, member)
            else:
                count = target.getRoleMemberCount(role)
                with multicall:
                    members = [target.getRoleMember(role, i) for i in range(count)]

                if not target.hasRole(role, expected_addrs_per_setting):
                    C.print(
                        f"Grant role {role} in {contract_name} for {expected_addrs_per_setting}\n"
                    )
                    target.grantRole(role, expected_addrs_per_setting)

                C.print(
                    f"Role {role} in {contract_name} has {count} members, checking against target config...\n"
                )

                for member in members:
                    if member != expected_addrs_per_setting:
                        C.print(f"Revoke role {role} in {contract_name} for {member}\n")
                        target.revokeRole(role, member)

    if not sim:
        safe.post_safe_tx()
    else:
        safe.post_safe_tx(skip_preview=True)
