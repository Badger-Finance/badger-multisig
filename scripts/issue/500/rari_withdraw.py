from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface
from dotmap import DotMap


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)

    fwbtc = interface.IFToken(registry.eth.rari['fWBTC-22'], owner=safe.account)
    fusdc = interface.IFToken(registry.eth.rari['fUSDC-22'], owner=safe.account)

    amount_fusdc = int(fusdc.balanceOf(safe) * 0.75)
    amount_fwbtc = int(fwbtc.balanceOf(safe) * 0.75)
    tx_data_usdc = fusdc.redeem.encode_input(amount_fusdc)
    tx_data_wbtc = fwbtc.redeem.encode_input(amount_fwbtc)

    txs = [
        DotMap({
            'receiver': fusdc.address,
            'value': 0,
            'input': tx_data_usdc,
        }),
        DotMap({
            'receiver': fwbtc.address,
            'value': 0,
            'input': tx_data_wbtc
        })
    ]

    safe_multi_tx = safe.multisend_from_receipts(txs)

    safe.post_transaction(safe_multi_tx)
