import pytest


@pytest.fixture(scope='function', autouse=True)
def deposited(safe, curve, convex, threepool_lp, convex_threepool_lp,USDC):
    amount = 10000 * 10 ** USDC.decimals()
    curve.deposit(threepool_lp, amount, USDC)
    amount = threepool_lp.balanceOf(safe)
    before = convex_threepool_lp.balanceOf(safe)
    convex.deposit(threepool_lp, amount)
    assert convex_threepool_lp.balanceOf(safe) > before
    

def test_withdraw(safe, convex, threepool_lp, convex_threepool_lp):
    before_bal_curve_lp = threepool_lp.balanceOf(safe)
    before_bal_convex_lp = convex_threepool_lp.balanceOf(safe)

    amount = convex_threepool_lp.balanceOf(safe)
    convex.withdraw(threepool_lp, amount)

    assert threepool_lp.balanceOf(safe) == before_bal_curve_lp + amount
    assert convex_threepool_lp.balanceOf(safe) == before_bal_convex_lp - amount

def test_withdraw_all(safe, convex, threepool_lp, convex_threepool_lp):
    before_bal_curve_lp = threepool_lp.balanceOf(safe)
    before_bal_convex_lp = convex_threepool_lp.balanceOf(safe)

    amount = convex_threepool_lp.balanceOf(safe)
    convex.withdraw_all(threepool_lp)

    assert threepool_lp.balanceOf(safe) == before_bal_curve_lp + amount
    assert convex_threepool_lp.balanceOf(safe) == before_bal_convex_lp - amount