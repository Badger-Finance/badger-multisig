import pytest
from brownie import chain
import brownie


def test_deposit_and_stake(safe, balancer, wbtc, weth, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(safe)
    bal_before_weth = weth.balanceOf(safe)
    bal_before_wbtc = wbtc.balanceOf(safe)

    underlyings = [wbtc, weth]
    amounts = [wbtc.balanceOf(safe), weth.balanceOf(safe)]

    balancer.deposit_and_stake(underlyings, amounts)

    assert wbtc.balanceOf(safe) < bal_before_weth
    assert weth.balanceOf(safe) < bal_before_wbtc
    assert staked_bpt.balanceOf(safe) > bal_before_staked_bpt
    chain.reset()


def test_deposit_and_stake_wrong_order(safe, balancer, wbtc, weth, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(safe)
    bal_before_weth = weth.balanceOf(safe)
    bal_before_wbtc = wbtc.balanceOf(safe)

    underylings = [weth, wbtc]
    amounts = [weth.balanceOf(safe), wbtc.balanceOf(safe)]

    balancer.deposit_and_stake(underylings, amounts)

    assert wbtc.balanceOf(safe) < bal_before_weth
    assert weth.balanceOf(safe) < bal_before_wbtc
    assert staked_bpt.balanceOf(safe) > bal_before_staked_bpt
    chain.reset()


# single asset deposit calc leaves dust
def test_deposit_and_stake_single_asset(safe, balancer, wbtc, bpt, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(safe)
    before_bal_wbtc = wbtc.balanceOf(safe)
    amount_wbtc = 1e8

    balancer.deposit_and_stake_single_asset(
        wbtc,
        amount_wbtc,
        bpt
    )

    # 1.01 multiplier to account for dust left in single asset deposit
    assert wbtc.balanceOf(safe) < (before_bal_wbtc - amount_wbtc) * 1.01
    assert staked_bpt.balanceOf(safe) > bal_before_staked_bpt

    chain.reset()


# revert: BAL#506, src: StableMath.calcBptOutGivenExactTokensIn
# possibly due to the balpy module not supporting more than 2 pools:
# https://github.com/balancer-labs/balpy/blob/a907f7b984f4e3ba3460a1ef064003d95da5e884/balpy/balancerv2cad/src/balancerv2cad/StablePool.py#L33-L40
def test_deposit_and_stake_threepool(safe, balancer, dai, threepool_bpt, threepool_staked_bpt):
    bal_before_staked_bpt = threepool_staked_bpt.balanceOf(safe)
    bal_before_dai = dai.balanceOf(safe)
    
    with pytest.raises(NotImplementedError):
        with brownie.reverts():
            balancer.deposit_and_stake_single_asset(
                dai,
                dai.balanceOf(safe) / 4,
                threepool_bpt
            )

            assert dai.balanceOf(safe) < bal_before_dai
            assert threepool_staked_bpt.balanceOf(safe) > bal_before_staked_bpt

    chain.reset()


def test_deposit_and_stake_weighted(safe, balancer, dai, weighted_bpt, weighted_staked_bpt):
    bal_before_staked_bpt = weighted_staked_bpt.balanceOf(safe)
    bal_before_dai = dai.balanceOf(safe)

    balancer.deposit_and_stake_single_asset(
        dai,
        1000e18,
        weighted_bpt
    )

    assert dai.balanceOf(safe) < bal_before_dai
    assert weighted_staked_bpt.balanceOf(safe) > bal_before_staked_bpt
    chain.reset()


# balancer.deposit_and_stake_single_asset still needs support for sending
# native ether opposed to erc20 only
def test_deposit_and_stake_weighted_eth(safe, balancer, dai, weth, weighted_bpt, weighted_staked_bpt):
    bal_before_staked_bpt = weighted_staked_bpt.balanceOf(safe)
    bal_before_eth = safe.account.balance()
    bal_before_dai = dai.balanceOf(safe)
    
    amount_dai = 10_000e18
    amount_eth = 10e18

    with brownie.reverts():
        balancer.deposit_and_stake(
            [dai, weth],
            [int(1e18), 100],
            pool=weighted_bpt,
            is_eth=True
        )

        assert dai.balanceOf(dai) == bal_before_dai - amount_dai
        assert safe.account.balance() == bal_before_eth - amount_eth
        assert weighted_staked_bpt.balanceOf(safe) > bal_before_staked_bpt

    chain.reset()
