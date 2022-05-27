from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    ibbtc_msig = GreatApeSafe(registry.eth.badger_wallets.ibbtc_multisig)

    bcvx = interface.ISettV4h(registry.eth.treasury_tokens.bCVX)
    bvecvx = interface.ISettV4h(registry.eth.treasury_tokens.bveCVX)
    bcvxcrv = interface.ISettV4h(registry.eth.treasury_tokens.bcvxCRV)

    ibbtc_msig.take_snapshot(tokens=[
        bcvx.address, bvecvx.address, bcvxcrv.address
    ])

    ibbtc_msig.init_badger()
    ibbtc_msig.badger.claim_all()

    ibbtc_msig.post_safe_tx()
