from rich.console import Console
from brownie import interface, chain, Contract, accounts
from helpers.addresses import registry

CONSOLE = Console()

ACCOUNT_TO_LOAD = ""


def main(broadcast="true"):
    dev = accounts.load(ACCOUNT_TO_LOAD)

    safe = interface.IMultisigWalletWithDailyLimit(
        registry.arbitrum.badger_wallets.dev_multisig_deprecated
    )

    bDXS = Contract(registry.arbitrum.sett_vaults.bdxsSwaprWeth)

    calldata_withdraw_all = bDXS.withdrawAll.encode_input()

    CONSOLE.print(
        f" === Calldata for withdrawing all bdxsSwaprWeth holdings =[blue]{calldata_withdraw_all}[/blue]. Target:[blue]{bDXS.address}[/blue] === \n"
    )

    if broadcast == "true":
        safe.submitTransaction(bDXS.address, 0, calldata_withdraw_all, {"from": dev})
