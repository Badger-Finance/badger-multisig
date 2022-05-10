import pytest
from brownie import chain


def test_deposit_and_stake(dev, balancer, wbtc, weth, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(dev)
    bal_before_weth = weth.balanceOf(dev)
    bal_before_wbtc = wbtc.balanceOf(dev)

    underlyings = [wbtc, weth]
    amounts = [wbtc.balanceOf(dev), weth.balanceOf(dev)]

    balancer.deposit_and_stake(underlyings, amounts)

    assert wbtc.balanceOf(dev) < bal_before_weth
    assert weth.balanceOf(dev) < bal_before_wbtc
    assert staked_bpt.balanceOf(dev) > bal_before_staked_bpt
    chain.reset()


def test_deposit_and_stake_wrong_order(dev, balancer, wbtc, weth, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(dev)
    bal_before_weth = weth.balanceOf(dev)
    bal_before_wbtc = wbtc.balanceOf(dev)

    underylings = [weth, wbtc]
    amounts = [weth.balanceOf(dev), wbtc.balanceOf(dev)]

    balancer.deposit_and_stake(underylings, amounts)

    assert wbtc.balanceOf(dev) < bal_before_weth
    assert weth.balanceOf(dev) < bal_before_wbtc
    assert staked_bpt.balanceOf(dev) > bal_before_staked_bpt
    chain.reset()


@pytest.mark.xfail
# single asset deposit calc leaves dust
def test_deposit_and_stake_single_asset(dev, balancer, wbtc, bpt, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(dev)

    balancer.deposit_and_stake_single_asset(
        wbtc,
        wbtc.balanceOf(dev),
        bpt
    )

    # fails - single asset calc leaves dust
    assert wbtc.balanceOf(dev) == 0
    assert staked_bpt.balanceOf(dev) > bal_before_staked_bpt
    chain.reset()


@pytest.mark.xfail
# revert: BAL#506, src: StableMath.calcBptOutGivenExactTokensIn
# possibly due to the balpy module not supporting more than 2 pools:
# https://github.com/balancer-labs/balpy/blob/a907f7b984f4e3ba3460a1ef064003d95da5e884/balpy/balancerv2cad/src/balancerv2cad/StablePool.py#L33-L40
def test_deposit_and_stake_threepool(dev, balancer, dai, threepool_bpt, threepool_staked_bpt):
    bal_before_staked_bpt = threepool_staked_bpt.balanceOf(dev)
    bal_before_dai = dai.balanceOf(dev)

    balancer.deposit_and_stake_single_asset(
        dai,
        dai.balanceOf(dev) / 4,
        threepool_bpt
    )

    assert dai.balanceOf(dev) < bal_before_dai
    assert threepool_staked_bpt.balanceOf(dev) > bal_before_staked_bpt
    chain.reset()


def test_deposit_and_stake_weighted(dev, balancer, dai, weighted_bpt, weighted_staked_bpt):
    bal_before_staked_bpt = weighted_staked_bpt.balanceOf(dev)
    bal_before_dai = dai.balanceOf(dev)

    balancer.deposit_and_stake_single_asset(
        dai,
        dev.account.balance(),
        weighted_bpt
    )

    assert dai.balanceOf(dev) < bal_before_dai
    assert weighted_staked_bpt.balanceOf(dev) > bal_before_staked_bpt
    chain.reset()


@pytest.mark.xfail
# balancer.deposit_and_stake_single_asset still needs support for sending
# native ether opposed to erc20 only
def test_deposit_and_stake_weighted_eth(dev, balancer, dai, weighted_bpt, weighted_staked_bpt):
    bal_before_staked_bpt = weighted_staked_bpt.balanceOf(dev)
    bal_before_eth = dev.account.balance()

    balancer.deposit_and_stake_single_asset(
        dai,
        dev.account.balance(),
        weighted_bpt,
        is_eth=True
    )

    assert dev.account.balance() < bal_before_eth
    assert weighted_staked_bpt.balanceOf(dev) > bal_before_staked_bpt
    chain.reset()
