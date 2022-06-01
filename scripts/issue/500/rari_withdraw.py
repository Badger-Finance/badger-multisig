from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface


safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)


def withdraw_udsc():
    fusdc = interface.IFToken(registry.eth.rari['fUSDC-22'], owner=safe.account)

    amount_fusdc = int(fusdc.balanceOf(safe) * 0.75)
    tx_data = fusdc.redeem.encode_input(amount_fusdc)

    safe_tx = safe.build_multisig_tx(
        to=registry.fusdc.address, value=0, data=tx_data, operation=1
    )

    safe.post_transaction(safe_tx)


def withdraw_wbtc():
    fwbtc = interface.IFToken(registry.eth.rari['fWBTC-22'], owner=safe.account)

    amount_fwbtc = int(fwbtc.balanceOf(safe) * 0.75)
    tx_data = fwbtc.redeem.encode_input(amount_fwbtc)

    safe_tx = safe.build_multisig_tx(
        to=registry.fwbtc.address, value=0, data=tx_data, operation=1
    )

    safe.post_transaction(safe_tx)
