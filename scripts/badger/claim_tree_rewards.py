from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main(msig='treasury_ops_multisig'):
    safe = GreatApeSafe(registry.eth.badger_wallets[msig])

    bcvx = safe.contract(registry.eth.treasury_tokens.bCVX)
    bvecvx = safe.contract(registry.eth.treasury_tokens.bveCVX)
    bcvxcrv = safe.contract(registry.eth.treasury_tokens.bcvxCRV)
    gravi = safe.contract(registry.eth.sett_vaults.graviAURA)

    safe.take_snapshot(tokens=[bcvx, bvecvx, bcvxcrv, gravi])

    safe.init_badger()
    safe.badger.claim_all()

    safe.post_safe_tx()
