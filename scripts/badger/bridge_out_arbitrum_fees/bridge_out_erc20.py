from rich.console import Console
from brownie import interface, accounts, Contract
from helpers.addresses import registry

CONSOLE = Console()

# tokens to bridge out
tokens_out = ["CRV", "USDT", "SUSHI", "WBTC"]

ACCOUNT_TO_LOAD = ""


def main(broadcast="true"):
    dev = accounts.load(ACCOUNT_TO_LOAD)

    safe = interface.IMultisigWalletWithDailyLimit(
        registry.arbitrum.badger_wallets.dev_multisig_deprecated
    )

    gateway = Contract(registry.arbitrum.arbitrum_gateway_router)

    for key in tokens_out:
        CONSOLE.print(f"[green] Processing calldata for {key}...[/green]")

        token = interface.IERC20(registry.arbitrum.treasury_tokens[key])

        token_balance = token.balanceOf(safe)

        if token_balance > 0:
            calldata_approve = token.approve.encode_input(
                gateway.address, token_balance
            )

            calldata_bridging = gateway.outboundTransfer.encode_input(
                registry.arbitrum.treasury_tokens[f"{key}"],
                registry.eth.badger_wallets.treasury_ops_multisig,
                token_balance,
                bytes("", encoding="UTF-8"),
            )

            CONSOLE.print(
                f" === Calldata for {key} transfer to L1. Amount: [red]{token_balance/10**token.decimals()}[/red] ==="
            )
            CONSOLE.print(
                f" === CALLDATA approve=[blue]{calldata_approve}[/blue] . Target:[blue]{token.address}[/blue] === \n"
            )
            CONSOLE.print(
                f" === CALLDATA Bridging=[blue]{calldata_bridging}[/blue] . Target:[blue]{gateway.address}[/blue] === \n"
            )

            if broadcast == "true":
                safe.submitTransaction(
                    token.address, 0, calldata_approve, {"from": dev}
                )
                safe.submitTransaction(
                    gateway.address, 0, calldata_bridging, {"from": dev}
                )
        else:
            CONSOLE.print(f" === Balance for {key} is zero === \n")
