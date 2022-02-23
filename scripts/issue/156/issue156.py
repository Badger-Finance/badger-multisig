from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface


def main():
    """
    deposit all bveCVX lp to bbveCVX sett
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)

    bvecvx_cvx_lp = interface.ICurveLP(
        registry.eth.treasury_tokens['bveCVX-CVX-f'],
        owner=safe.account
)
    bbveCVX_sett = interface.ISettV4h(
        registry.eth.sett_vaults['bbveCVX-CVX-f'],
        owner=safe.account
    )

    safe.take_snapshot(tokens=[bvecvx_cvx_lp.address, bbveCVX.address])

    bvecvx_cvx_lp.approve(bbveCVX_sett, bvecvx_cvx_lp.balanceOf(safe))
    bbveCVX_sett.depositAll()

    safe.print_snapshot()

    safe.post_safe_tx()
