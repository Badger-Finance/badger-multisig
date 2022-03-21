from rich.console import Console
from brownie import interface, accounts, Contract
from helpers.addresses import registry

ACCOUNT_TO_LOAD = ""


def main(broadcast="true"):
    dev = accounts.load(ACCOUNT_TO_LOAD)

    safe = interface.IMultisigWalletWithDailyLimit(
        registry.arbitrum.badger_wallets.dev_multisig_deprecated
    )

    reward_logger = Contract(registry.arbitrum.rewardsLogger)

    ADMIN_ROLE = reward_logger.DEFAULT_ADMIN_ROLE()

    # revoke admin role from deprecated dev_msig addr
    encode_input_revoke_role_admin = reward_logger.revokeRole.encode_input(
        ADMIN_ROLE, safe.address
    )

    print(f"encode_input_revoke_admin_role={encode_input_revoke_role_admin}\n")

    if broadcast == "true":
        safe.submitTransaction(
            reward_logger.address,
            0,
            encode_input_revoke_role_admin,
            {"from": dev},
        )
        safe.submitTransaction(
            registry.arbitrum.badger_wallets.badgertree,
            0,
            encode_input_revoke_role_admin,
            {"from": dev},
        )
        safe.submitTransaction(
            registry.arbitrum.KeeperAccessControl,
            0,
            encode_input_revoke_role_admin,
            {"from": dev},
        )
