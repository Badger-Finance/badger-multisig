from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface


def main():
    """
    deposit all bveCVX lp to bbveCVX sett
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)

    bveCVX = interface.ICurveLP(
        registry.eth.treasury_tokens['bveCVX-CVX-f'],
        owner=safe.account
)
    bbveCVX = interface.ISettV4h(
        registry.eth.sett_vaults['bbveCVX-CVX-f'],
        owner=safe.account
    )

    bveCVX.approve(bbveCVX, bveCVX.balanceOf(safe))
    bbveCVX.depositAll()

    safe.post_safe_tx()
