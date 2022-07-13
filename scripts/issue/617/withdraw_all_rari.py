from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface
from rich.pretty import pprint
from dotmap import DotMap


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)

    fusdc = interface.IFToken(registry.eth.rari['fUSDC-22'], owner=safe.account)
    fwbtc = interface.IFToken(registry.eth.rari['fWBTC-22'], owner=safe.account)

    usdc_withdrawable = fusdc.getCash()
    wbtc_withdrawable = fwbtc.getCash()

    pprint(f'withdrawing {usdc_withdrawable / 1e6} usdc')
    pprint(f'withdrawing {wbtc_withdrawable / 1e8} wbtc')

    receipts = [
        DotMap({
            'receiver': fusdc.address,
            'value': 0,
            'input': fusdc.redeemUnderlying.encode_input(usdc_withdrawable),
        }),
        DotMap({
            'receiver': fwbtc.address,
            'value': 0,
            'input': fwbtc.redeemUnderlying.encode_input(wbtc_withdrawable)
        })
    ]

    safe_tx = safe.multisend_from_receipts(receipts=receipts)
    pprint(safe_tx.__dict__)

    safe.post_transaction(safe_tx)