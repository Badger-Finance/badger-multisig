from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    """
    retrieve the $cvx that got unlocked by the vlcvx locker and send it back to
    the vault for user withdrawal
    https://github.com/GalloDaSballo/vested-cvx/blob/main/tests/test_roleplay_unlock.py
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    bvecvx_vault = GreatApeSafe(registry.eth.sett_vaults.bveCVX)
    bvecvx_strat = interface.IVestedCvx(
        registry.eth.strategies['native.vestedCVX'],
        owner=safe.account
    )
    cvx = interface.IERC20(registry.eth.treasury_tokens.CVX)

    bvecvx_vault.take_snapshot(tokens=[cvx.address])

    bvecvx_strat.manualProcessExpiredLocks()
    bvecvx_strat.manualSendCVXToVault()

    bvecvx_vault.print_snapshot()

    safe.post_safe_tx()
