from rich.console import Console
from brownie import interface, Contract, accounts
from helpers.addresses import registry

CONSOLE = Console()

ACCOUNT_TO_LOAD = ""

# will transfer WETH & BADGER to techops for ops & future emissions
def main(broadcast="true", token="WETH"):
    dev = accounts.load(ACCOUNT_TO_LOAD)

    safe = interface.IMultisigWalletWithDailyLimit(
        registry.arbitrum.badger_wallets.dev_multisig_deprecated
    )

    token_contract = Contract(registry.arbitrum.treasury_tokens[token])

    calldata_transfer = token_contract.transfer.encode_input(
        registry.arbitrum.badger_wallets.techops_multisig,
        token_contract.balanceOf(safe),
    )

    CONSOLE.print(
        f" === Calldata for [green]{token.symbol()}[/green] transfer to techops=[blue]{calldata_transfer}[/blue]. Target:[blue]{token_contract.address}[/blue] === \n"
    )

    if broadcast == "true":
        safe.submitTransaction(
            token_contract.address, 0, calldata_transfer, {"from": dev}
        )
