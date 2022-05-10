import pytest
from brownie import chain


@pytest.fixture()
def deposited_weighted(dev, balancer, wbtc, weth, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(dev)
    assert bal_before_staked_bpt == 0

    underylings = [wbtc, weth]
    amounts = [wbtc.balanceOf(dev), weth.balanceOf(dev)]

    balancer.deposit_and_stake(underylings, amounts)

    assert wbtc.balanceOf(dev) == 0
    assert weth.balanceOf(dev) == 0
    assert staked_bpt.balanceOf(dev) > 0


@pytest.fixture()
def deposited_stable(dev, balancer, dai, threepool_bpt, threepool_staked_bpt):
    bal_before_staked_bpt = threepool_staked_bpt.balanceOf(dev)
    bal_before_dai = dai.balanceOf(dev)

    balancer.deposit_and_stake_single_asset(
        dai,
        dai.balanceOf(dev) / 4,
        threepool_bpt
    )

    assert dai.balanceOf(dev) < bal_before_dai
    assert threepool_staked_bpt.balanceOf(dev) > bal_before_staked_bpt


def test_unstake_and_withdraw_all_weighted(dev, balancer, wbtc, weth, bpt, staked_bpt, deposited_weighted):
    bal_before_weth = weth.balanceOf(dev)
    bal_before_wbtc = wbtc.balanceOf(dev)

    balancer.unstake_all_and_withdraw_all(pool=bpt)

    assert weth.balanceOf(dev) > bal_before_weth
    assert wbtc.balanceOf(dev) > bal_before_wbtc

    assert staked_bpt.balanceOf(dev) == 0
    assert bpt.balanceOf(dev) == 0


def test_unstake_and_withdraw_all_single_asset(dev, balancer, wbtc, bpt, staked_bpt, deposited_weighted):
    bal_before_wbtc = wbtc.balanceOf(dev)

    balancer.unstake_and_withdraw_all_single_asset(wbtc, pool=bpt)

    assert wbtc.balanceOf(dev) > bal_before_wbtc
    assert staked_bpt.balanceOf(dev) == 0
    assert bpt.balanceOf(dev) == 0


@pytest.mark.xfail(reason="Not implemented")
def test_unstake_and_withdraw_all_stable(dev, balancer, dai, threepool_bpt, threepool_staked_bpt):
    bal_before_dai = dai.balanceOf(dev)

    balancer.unstake_and_withdraw_all_single_asset(dai, pool=threepool_bpt)

    assert dai.balanceOf(dev) > bal_before_dai
    assert threepool_staked_bpt.balanceOf(dev) == 0
    assert threepool_bpt.balanceOf(dev) == 0
