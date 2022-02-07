from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    """
    issue 103; send more bvecvx to trops for arbing
    https://github.com/Badger-Finance/badger-multisig/issues/103
    """
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)

    bvecvx = interface.ISettV4h(
        registry.eth.treasury_tokens.bveCVX, owner=safe.account
    )

    safe.take_snapshot([bvecvx.address])
    trops.take_snapshot([bvecvx.address])

    bvecvx.transfer(trops, bvecvx.balanceOf(safe))

    safe.print_snapshot()
    trops.print_snapshot()

    safe.post_safe_tx()
