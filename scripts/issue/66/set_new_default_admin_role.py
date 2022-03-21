from rich.console import Console
from brownie import interface, accounts, Contract
from helpers.addresses import registry

C = Console()

# addresses involved
NEW_ADMIN = registry.arbitrum.badger_wallets.dev_multisig

ACCOUNT_TO_LOAD = ""

# Set admin_role in rewards logger, tree and keeper ACL
def main(broadcast="true"):
    dev = accounts.load(ACCOUNT_TO_LOAD)

    safe = interface.IMultisigWalletWithDailyLimit(
        registry.arbitrum.badger_wallets.dev_multisig_deprecated
    )

    reward_logger = Contract(registry.arbitrum.rewardsLogger)

    # admin role is '0x0000000000000000000000000000000000000000000000000000000000000000'
    DEFAULT_ADMIN_ROLE = reward_logger.DEFAULT_ADMIN_ROLE()
    
    # same encode output for all
    encode_input_grant_role_admin = reward_logger.grantRole.encode_input(
        DEFAULT_ADMIN_ROLE, NEW_ADMIN
    )

    print(f"encode_input_grant_admin_role={encode_input_grant_role_admin}\n")

    if broadcast == "true":
        safe.submitTransaction(
            reward_logger.address,
            0,
            encode_input_grant_role_admin,
            {"from": dev},
        )
        safe.submitTransaction(
            registry.arbitrum.badger_wallets.badgertree, 0, encode_input_grant_role_admin, {"from": dev}
        )
        safe.submitTransaction(
            registry.arbitrum.KeeperAccessControl, 0, encode_input_grant_role_admin, {"from": dev}
        )
