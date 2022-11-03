import pytest
import brownie


def test_deposit_given_amounts(safe, curve, threepool_lptoken, USDC):
    before_bal_3crv = threepool_lptoken.balanceOf(safe)
    before_bal_usdc = USDC.balanceOf(safe)

    amount_usdc = 100_000 * 10 ** USDC.decimals()
    amounts = [0, amount_usdc, 0]
    curve.deposit(threepool_lptoken, amounts)

    assert threepool_lptoken.balanceOf(safe) > before_bal_3crv
    assert USDC.balanceOf(safe) == before_bal_usdc - amounts[1]


def test_deposit_given_token(safe, curve, threepool_lptoken, USDC):
    before_bal_3crv = threepool_lptoken.balanceOf(safe)
    before_bal_usdc = USDC.balanceOf(safe)

    amount = 100_000 * 10 ** USDC.decimals()
    curve.deposit(threepool_lptoken, amount, USDC)

    assert threepool_lptoken.balanceOf(safe) > before_bal_3crv
    assert USDC.balanceOf(safe) < before_bal_usdc


def test_deposit_no_token_specified(curve, threepool_lptoken, USDC):
    amount = 100_000 * 10 ** USDC.decimals()

    with brownie.reverts():
        curve.deposit(threepool_lptoken, amount)
