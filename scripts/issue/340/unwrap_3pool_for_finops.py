from brownie import Contract, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    payments = GreatApeSafe(registry.eth.badger_wallets.payments_multisig)
    threepool = safe.contract(registry.eth.treasury_tokens.crv3pool)
    usdc = interface.ERC20(registry.eth.treasury_tokens.USDC, owner=safe.account)

    safe.take_snapshot([threepool, usdc])
    payments.take_snapshot([threepool, usdc])
    safe.init_curve()
    safe.curve.withdraw_to_one_coin(threepool, 50_000e18, usdc)
    print(usdc.balanceOf(safe))
    usdc.transfer(payments, 50_000e6)
    safe.print_snapshot()
    payments.print_snapshot()
    safe.post_safe_tx()
