import pytest
from brownie import chain

# Set up gives each test Convex LP tokens
@pytest.fixture(scope="function", autouse=True)
def deposited(safe, curve, convex, threepool_lp, USDC):
    amount = 10000 * 10 ** USDC.decimals()
    curve.deposit(threepool_lp, amount, USDC)
    amount = threepool_lp.balanceOf(safe)
    convex.deposit(threepool_lp, amount)


def test_claim_all(safe, convex, convex_threepool_reward):
    before_bal_rewards = convex_threepool_reward.balanceOf(safe)
    convex.claim_all()

    assert convex_threepool_reward.balanceOf(safe) > before_bal_rewards


def test_stake(safe, convex, convex_rewards, threepool_lp, convex_threepool_lp):
    before_bal_rewards = convex_rewards.balanceOf(safe)

    convex.stake(threepool_lp, convex_threepool_lp.balanceOf(safe))

    assert convex_threepool_lp.balanceOf(safe) == 0
    assert convex_rewards.balanceOf(safe) > before_bal_rewards


def test_stake_all(safe, convex, convex_rewards, threepool_lp, convex_threepool_lp):
    before_bal_rewards = convex_rewards.balanceOf(safe)

    convex.stake_all(threepool_lp)

    assert convex_threepool_lp.balanceOf(safe) == 0
    assert convex_rewards.balanceOf(safe) > before_bal_rewards


def test_unstake(
    safe,
    convex,
    convex_rewards,
    threepool_lp,
    convex_threepool_lp,
    convex_threepool_reward,
):
    convex.stake(threepool_lp, convex_threepool_lp.balanceOf(safe))
    before_bal_staked = convex_rewards.balanceOf(safe)
    before_bal_convex_lp = convex_threepool_lp.balanceOf(safe)
    before_bal_reward = convex_threepool_reward.balanceOf(safe)

    # ensure rewards are available
    chain.sleep(100)
    chain.mine()

    convex.unstake(threepool_lp, before_bal_staked)

    assert convex_rewards.balanceOf(safe) == 0
    assert (
        convex_threepool_lp.balanceOf(safe) == before_bal_convex_lp + before_bal_staked
    )
    assert convex_threepool_reward.balanceOf(safe) > before_bal_reward


def test_unstake_all(
    safe,
    convex,
    convex_rewards,
    threepool_lp,
    convex_threepool_lp,
    convex_threepool_reward,
):
    convex.stake(threepool_lp, convex_threepool_lp.balanceOf(safe))
    before_bal_staked = convex_rewards.balanceOf(safe)
    before_bal_convex_lp = convex_threepool_lp.balanceOf(safe)
    before_bal_reward = convex_threepool_reward.balanceOf(safe)

    chain.sleep(100)
    chain.mine()

    convex.unstake_all(threepool_lp)

    assert convex_rewards.balanceOf(safe) == 0
    assert (
        convex_threepool_lp.balanceOf(safe) == before_bal_convex_lp + before_bal_staked
    )
    assert convex_threepool_reward.balanceOf(safe) > before_bal_reward


def test_unstake_and_withdraw(
    safe,
    convex,
    convex_rewards,
    threepool_lp,
    convex_threepool_lp,
    convex_threepool_reward,
):
    convex.stake(threepool_lp, convex_threepool_lp.balanceOf(safe))
    before_bal_staked = convex_rewards.balanceOf(safe)
    before_bal_reward = convex_threepool_reward.balanceOf(safe)
    before_bal_threepool = threepool_lp.balanceOf(safe)

    chain.sleep(100)
    chain.mine()

    convex.unstake_and_withdraw(threepool_lp, before_bal_staked)

    assert convex_rewards.balanceOf(safe) == 0
    assert convex_threepool_lp.balanceOf(safe) == 0
    assert convex_threepool_reward.balanceOf(safe) > before_bal_reward
    assert threepool_lp.balanceOf(safe) > before_bal_threepool


def test_unstake_all_and_withdraw_all(
    safe,
    convex,
    convex_rewards,
    threepool_lp,
    convex_threepool_lp,
    convex_threepool_reward,
):
    convex.stake(threepool_lp, convex_threepool_lp.balanceOf(safe))
    before_bal_reward = convex_threepool_reward.balanceOf(safe)
    before_bal_threepool = threepool_lp.balanceOf(safe)

    chain.sleep(100)
    chain.mine()

    convex.unstake_all_and_withdraw_all(threepool_lp)

    assert convex_rewards.balanceOf(safe) == 0
    assert convex_threepool_lp.balanceOf(safe) == 0
    assert convex_threepool_reward.balanceOf(safe) > before_bal_reward
    assert threepool_lp.balanceOf(safe) > before_bal_threepool
