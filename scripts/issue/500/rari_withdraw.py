from brownie import interface
from dotmap import DotMap
from rich.pretty import pprint

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


SAFE = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)


def main():
    fusdc = interface.IFToken(registry.eth.rari["fUSDC-22"], owner=SAFE.account)
    fwbtc = interface.IFToken(registry.eth.rari["fWBTC-22"], owner=SAFE.account)

    amount_fusdc = int(fusdc.balanceOf(SAFE) * 0.75)
    amount_fwbtc = int(fwbtc.balanceOf(SAFE) * 0.75)

    receipts = [
        DotMap(
            {
                "receiver": fusdc.address,
                "value": 0,
                "input": fusdc.redeem.encode_input(amount_fusdc),
            }
        ),
        DotMap(
            {
                "receiver": fwbtc.address,
                "value": 0,
                "input": fwbtc.redeem.encode_input(amount_fwbtc),
            }
        ),
    ]

    safe_tx = SAFE.multisend_from_receipts(receipts=receipts)
    pprint(safe_tx.__dict__)

    SAFE.post_transaction(safe_tx)
