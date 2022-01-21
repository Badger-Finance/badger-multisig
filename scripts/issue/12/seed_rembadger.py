from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


TO_SEED = 600_000


def main():
    """
    seed rembadger vault with 600k $badger
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    rembadger = interface.IRemBadger(registry.eth.sett_vaults.remBADGER)
    verifier = interface.IBalanceVerifier(
        registry.eth.helpers.balance_checker, owner=safe.account
    )
    badger = interface.ERC20(
        registry.eth.treasury_tokens.BADGER, owner=safe.account
    )

    safe.take_snapshot(tokens=[badger.address])

    mantissa = TO_SEED * 10 ** badger.decimals()
    assert badger.balanceOf(safe) >= mantissa

    # get current balance of rembadger vault
    bal_before = badger.balanceOf(rembadger)
    pps_before = rembadger.getPricePerFullShare()

    # transfer
    badger.approve(rembadger, mantissa)
    badger.transfer(rembadger, mantissa)

    # make sure it arrived
    verifier.verifyBalance(badger, rembadger, mantissa + bal_before)

    # make sure pps increased
    assert rembadger.getPricePerFullShare() > pps_before

    safe.post_safe_tx()
