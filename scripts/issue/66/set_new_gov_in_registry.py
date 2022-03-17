from rich.console import Console
from brownie import interface, accounts, Contract
from helpers.addresses import registry

C = Console()

# addresses involved
NEW_GOV = registry.arbitrum.badger_wallets.dev_multisig

ACCOUNT_TO_LOAD = ""


def main(broadcast="true"):
    dev = accounts.load(ACCOUNT_TO_LOAD)

    safe = interface.IMultisigWalletWithDailyLimit(
        registry.arbitrum.badger_wallets.dev_multisig_deprecated
    )

    registry_contract = Contract(registry.arbitrum.registry)

    encode_input = registry_contract.setGovernance.encode_input(NEW_GOV)

    print(f"Set governance in registry, encode_input={encode_input}\n")

    if broadcast == "true":
        safe.submitTransaction(
            registry_contract.address, 0, encode_input, {"from": dev}
        )
