from rich.console import Console
from brownie import interface
from helpers.addresses import registry
from great_ape_safe import GreatApeSafe

CONSOLE = Console()

# tokens to bridge out
tokens_out = [
    registry.arbitrum.treasury_tokens.CRV,
    registry.arbitrum.treasury_tokens.USDT,
    registry.arbitrum.treasury_tokens.SUSHI,
    registry.arbitrum.treasury_tokens.WBTC
    ]


def main():
    safe = GreatApeSafe(registry.arbitrum.badger_wallets.dev_multisig)
    gateway = safe.contract(registry.arbitrum.arbitrum_gateway_router)

    for address in tokens_out:
        token = interface.IERC20(address, owner=safe.address)
        token_balance = token.balanceOf(safe)

        if token_balance > 0:
            token.approve(gateway.address, token_balance)

            gateway.outboundTransfer(
                address,
                registry.eth.badger_wallets.treasury_ops_multisig,
                token_balance,
                bytes("", encoding="UTF-8"),
            )

        else:
            CONSOLE.print(f" === Balance for {token.symbol()} is zero === \n")

    safe.post_safe_tx()
