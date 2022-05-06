import pytest


@pytest.fixture(autouse=True)
def deposited(dev, balancer, wbtc, weth, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(dev)
    assert bal_before_staked_bpt == 0

    underylings = [wbtc, weth]
    amounts = [wbtc.balanceOf(dev), weth.balanceOf(dev)]

    balancer.deposit_and_stake(underylings, amounts)

    assert wbtc.balanceOf(dev) == 0
    assert weth.balanceOf(dev) == 0
    assert staked_bpt.balanceOf(dev) > 0


def test_unstake_and_withdraw_all(dev, balancer, wbtc, weth, bpt, staked_bpt):
    bal_before_weth = weth.balanceOf(dev)
    bal_before_wbtc = wbtc.balanceOf(dev)
    bal_before_bpt = bpt.balanceOf(dev)

    balancer.unstake_all_and_withdraw_all(pool=bpt)

    assert weth.balanceOf(dev) > bal_before_weth
    assert wbtc.balanceOf(dev) > bal_before_wbtc

    assert staked_bpt.balanceOf(dev) == 0
    assert bpt.balanceOf(dev) < bal_before_bpt


def test_unstake_and_withdraw_all_single_asset(dev, balancer, wbtc, bpt, staked_bpt):
    bal_before_wbtc = wbtc.balanceOf(dev)
    bal_before_bpt = bpt.balanceOf(dev)

    balancer.unstake_and_withdraw_all_single_asset(wbtc, pool=bpt)

    assert wbtc.balanceOf(dev) > bal_before_wbtc

    assert staked_bpt.balanceOf(dev) == 0
    assert bpt.balanceOf(dev) < bal_before_bpt
