from rich.console import Console
from brownie import interface, accounts, Contract
from helpers.addresses import registry

C = Console()

# addresses involved
NEW_OWNER = registry.arbitrum.badger_wallets.dev_multisig

ACCOUNT_TO_LOAD = ""


def main(broadcast="true"):
    dev = accounts.load(ACCOUNT_TO_LOAD)

    safe = interface.IMultisigWalletWithDailyLimit(
        registry.arbitrum.badger_wallets.dev_multisig_deprecated
    )

    proxy_timelock = Contract(registry.arbitrum.proxyAdminTimelock)

    proxy_admin_dev = Contract(registry.arbitrum.proxyAdminDev)

    encode_input_transfer_ownership = proxy_timelock.transferOwnership.encode_input(
        NEW_OWNER
    )

    print(f"encode_input for transfer ownership = {encode_input_transfer_ownership}\n")

    if broadcast == "true":
        safe.submitTransaction(
            proxy_timelock.address, 0, encode_input_transfer_ownership, {"from": dev}
        )
        safe.submitTransaction(
            proxy_admin_dev.address, 0, encode_input_transfer_ownership, {"from": dev}
        )
