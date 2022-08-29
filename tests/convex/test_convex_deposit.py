import pytest


@pytest.fixture(scope='function', autouse=True)
def deposited(curve, threepool_lp, USDC):
    amount = 10_000e6
    curve.deposit(threepool_lp, amount, USDC)

def test_deposit(safe, convex, threepool_lp, convex_threepool_lp):
    before_bal_convex_lp = convex_threepool_lp.balanceOf(safe)

    amount = threepool_lp.balanceOf(safe)
    convex.deposit(threepool_lp, amount)
    
    assert convex_threepool_lp.balanceOf(safe) > before_bal_convex_lp

def test_deposit_all(safe, convex, threepool_lp, convex_threepool_lp):
    before_bal_convex_lp = convex_threepool_lp.balanceOf(safe)

    convex.deposit_all(threepool_lp)
    
    assert convex_threepool_lp.balanceOf(safe) > before_bal_convex_lp

def test_deposit_and_stake(safe, convex, threepool_lp):
    (_,_,_,rewards) = convex.get_pool_info(threepool_lp)
    rewards = safe.contract(rewards)

    amount = threepool_lp.balanceOf(safe)
    before_bal_staked = rewards.balanceOf(safe)

    convex.deposit_and_stake(threepool_lp, amount)
    
    assert rewards.balanceOf(safe) > before_bal_staked

def test_deposit_all__and_stake(safe, convex, threepool_lp):
    (_,_,_,rewards) = convex.get_pool_info(threepool_lp)

    rewards = safe.contract(rewards)
    before_bal_staked = rewards.balanceOf(safe)

    convex.deposit_all_and_stake(threepool_lp)
    
    assert rewards.balanceOf(safe) > before_bal_staked