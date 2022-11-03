from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    payments = GreatApeSafe(registry.eth.badger_wallets.payments_multisig)
    balance_checker = interface.IBalanceChecker(
        registry.eth.helpers.balance_checker, owner=safe.account
    )
    usdc = interface.ERC20(registry.eth.treasury_tokens.USDC, owner=safe.account)
    ausdc = interface.ERC20(registry.eth.treasury_tokens.aUSDC, owner=safe.account)

    safe.take_snapshot([ausdc, usdc])
    payments.take_snapshot([ausdc, usdc])

    safe.init_aave()
    safe.aave.withdraw_all(usdc, payments)

    balance_checker.verifyBalance(usdc, payments, 1_300_000 * 10 ** usdc.decimals())

    safe.print_snapshot()
    payments.print_snapshot()
    safe.post_safe_tx()
