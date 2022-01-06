import pytest


def test_deposit_given_amounts(safe, curve, tripool_lptoken, USDC):
    before_bal_3crv = tripool_lptoken.balanceOf(safe)
    before_bal_usdc = USDC.balanceOf(safe)
    
    amount_usdc = 100_000 * 10**USDC.decimals()
    amounts = [0, amount_usdc, 0]
    curve.deposit(tripool_lptoken, amounts)

    assert tripool_lptoken.balanceOf(safe) > before_bal_3crv
    assert USDC.balanceOf(safe) == before_bal_usdc - amounts[1]
    
def test_deposit_given_token(safe, curve, tripool_lptoken, USDC):
    before_bal_3crv = tripool_lptoken.balanceOf(safe)
    before_bal_usdc = USDC.balanceOf(safe)
    
    amount = 100_000 * 10**USDC.decimals()
    curve.deposit(tripool_lptoken, amount, USDC)

    assert tripool_lptoken.balanceOf(safe) > before_bal_3crv
    assert USDC.balanceOf(safe) < before_bal_usdc

@pytest.mark.xfail
def test_deposit_no_token_specified(curve, tripool_lptoken, USDC):
    amount = 100_000 * 10**USDC.decimals()
    curve.deposit(tripool_lptoken, amount)
