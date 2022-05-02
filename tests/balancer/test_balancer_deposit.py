from brownie import chain


def test_deposit_and_stake(dev, balancer, wbtc, weth, bpt, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(dev)
    assert bal_before_staked_bpt == 0

    underylings = [wbtc, weth]
    amounts = [wbtc.balanceOf(dev), weth.balanceOf(dev)]

    balancer.deposit_and_stake(underylings, amounts)

    assert wbtc.balanceOf(dev) == 0
    assert weth.balanceOf(dev) == 0
    assert staked_bpt.balanceOf(dev) > 0
    chain.reset()


def test_deposit_and_stake_wrong_order(dev, balancer, wbtc, weth, bpt, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(dev)
    assert bal_before_staked_bpt == 0

    underylings = [weth, wbtc]
    amounts = [weth.balanceOf(dev), wbtc.balanceOf(dev)]

    balancer.deposit_and_stake(underylings, amounts)

    assert wbtc.balanceOf(dev) == 0
    assert weth.balanceOf(dev) == 0
    assert staked_bpt.balanceOf(dev) > 0
    chain.reset()


def test_deposit_only(dev, balancer, wbtc, weth, bpt):
    bal_before_bpt = bpt.balanceOf(dev)
    assert bal_before_bpt == 0

    underylings = [weth, wbtc]
    amounts = [weth.balanceOf(dev), wbtc.balanceOf(dev)]

    balancer.deposit_and_stake(underylings, amounts, stake=False)

    assert wbtc.balanceOf(dev) == 0
    assert weth.balanceOf(dev) == 0
    assert bpt.balanceOf(dev) > 0
    chain.reset()
