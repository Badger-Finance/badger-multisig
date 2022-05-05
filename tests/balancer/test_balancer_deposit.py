from brownie import chain


def test_deposit_and_stake(dev, balancer, wbtc, weth, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(dev)
    bal_before_weth = weth.balanceOf(dev)
    bal_before_wbtc = wbtc.balanceOf(dev)

    underylings = [wbtc, weth]
    amounts = [wbtc.balanceOf(dev), weth.balanceOf(dev)]

    balancer.deposit_and_stake(underylings, amounts)

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


def test_deposit_and_stake_single_asset(dev, balancer, wbtc, bpt, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(dev)
    bal_before_wbtc = wbtc.balanceOf(dev)

    balancer.deposit_and_stake_single_asset(
        wbtc,
        wbtc.balanceOf(dev),
        bpt
    )

    assert wbtc.balanceOf(dev) < bal_before_wbtc
    assert staked_bpt.balanceOf(dev) > bal_before_staked_bpt
    chain.reset()


def test_deposit_and_stake_threepool(dev, balancer, dai, threepool_bpt, threepool_staked_bpt):
    bal_before_staked_bpt = threepool_staked_bpt.balanceOf(dev)
    bal_before_dai = dai.balanceOf(dev)

    # revert: BAL#506, src: StableMath.calcBptOutGivenExactTokensIn
    balancer.deposit_and_stake_single_asset(
        dai,
        dai.balanceOf(dev),
        threepool_bpt
    )

    assert dai.balanceOf(dev) < bal_before_dai
    assert threepool_staked_bpt.balanceOf(dev) > bal_before_staked_bpt
    chain.reset()