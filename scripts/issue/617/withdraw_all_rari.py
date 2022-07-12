from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface
from rich.pretty import pprint


safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)


def withdraw_usdc():
    fusdc = interface.IFToken(registry.eth.rari['fUSDC-22'], owner=safe.account)

    amount_fusdc = fusdc.balanceOf(safe)
    pprint(f'withdrawing {amount_fusdc / 1e6} f-usdc')
    tx_data = fusdc.redeem.encode_input(amount_fusdc)

    safe_tx = safe.build_multisig_tx(
        to=registry.fusdc.address, value=0, data=tx_data, operation=1
    )

    pprint(safe_tx.__dict__)
    safe.post_transaction(safe_tx)


def withdraw_wbtc():
    fwbtc = interface.IFToken(registry.eth.rari['fWBTC-22'], owner=safe.account)

    amount_fwbtc = fwbtc.balanceOf(safe)
    pprint(f'withdrawing {amount_fwbtc / 1e8} f-wbtc')
    tx_data = fwbtc.redeem.encode_input(amount_fwbtc)

    safe_tx = safe.build_multisig_tx(
        to=registry.fwbtc.address, value=0, data=tx_data, operation=1
    )

    pprint(safe_tx.__dict__)
    safe.post_transaction(safe_tx)