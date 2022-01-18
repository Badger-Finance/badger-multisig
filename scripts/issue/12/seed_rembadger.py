from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    """
    seed rembadger vault with 600k $badger
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    rembadger = None # still has to be deployed
    verifier = interface.IBalanceVerifier(registry.eth.helpers.balance_checker)
    badger = interface.IERC20Metadata(
        registry.eth.treasury_tokens.BADGER, owner=safe.account
    )

    safe.take_snapshot(tokens=[badger.address])

    mantissa = 600_000 * 10 ** badger.decimals()
    assert badger.balanceOf(safe) >= mantissa

    # get current balance of rembadger vault
    bal_before = badger.balanceOf(rembadger)

    badger.approve(rembadger, mantissa)
    rembadger.addWant(mantissa)

    # make sure it arrived
    verifier.verifyBalance(badger, rembadger, mantissa + bal_before)

    safe.post_safe_tx()
