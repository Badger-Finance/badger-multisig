from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main(msig='treasury_ops_multisig'):
    safe = GreatApeSafe(registry.eth.badger_wallets[msig])

    bcvx = interface.ISettV4h(registry.eth.treasury_tokens.bCVX)
    bvecvx = interface.ISettV4h(registry.eth.treasury_tokens.bveCVX)
    bcvxcrv = interface.ISettV4h(registry.eth.treasury_tokens.bcvxCRV)

    safe.take_snapshot(tokens=[bcvx.address, bvecvx.address, bcvxcrv.address])

    safe.init_badger()
    safe.badger.claim_all()

    safe.post_safe_tx()
