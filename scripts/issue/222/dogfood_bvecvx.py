from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface


def main():
    """
    deposit all bveCVX lp to bbveCVX sett from trops on behalf of vault
    """

    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)

    bvecvx_cvx_lp = interface.ICurveLP(
        registry.eth.treasury_tokens["bveCVX-CVX-f"], owner=trops.account
    )
    bbveCVX_sett = interface.ISettV4h(
        registry.eth.sett_vaults["bbveCVX-CVX-f"], owner=trops.account
    )

    trops.take_snapshot(tokens=[bvecvx_cvx_lp.address, bbveCVX_sett.address])
    vault.take_snapshot(tokens=[bvecvx_cvx_lp.address, bbveCVX_sett.address])

    bvecvx_cvx_lp.approve(bbveCVX_sett, bvecvx_cvx_lp.balanceOf(trops))
    bbveCVX_sett.depositFor(vault, bvecvx_cvx_lp.balanceOf(trops))

    trops.print_snapshot()
    vault.print_snapshot()

    trops.post_safe_tx()
