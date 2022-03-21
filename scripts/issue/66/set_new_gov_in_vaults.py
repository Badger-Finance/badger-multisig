from rich.console import Console
from brownie import interface, accounts, Contract
from helpers.addresses import registry

C = Console()

# addresses involved
NEW_GOV = registry.arbitrum.badger_wallets.dev_multisig

setts = registry.arbitrum.sett_vaults

ACCOUNT_TO_LOAD = ""


def main(broadcast="true"):
    dev = accounts.load(ACCOUNT_TO_LOAD)

    safe = interface.IMultisigWalletWithDailyLimit(
        registry.arbitrum.badger_wallets.dev_multisig_deprecated
    )

    for key, addr in setts.items():

        sett = Contract(addr)
        
        if sett.governance() == safe.address:
            print(
                f"Current governance address is in ({key}) sett: {sett.governance()}\n"
            )

            encode_input = sett.setGovernance.encode_input(NEW_GOV)

            print(f"({key}), set governance, encode_input={encode_input}\n")

            if broadcast == "true":
                safe.submitTransaction(addr, 0, encode_input, {"from": dev})
