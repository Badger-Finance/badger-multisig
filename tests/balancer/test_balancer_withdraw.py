import pytest
import brownie


@pytest.fixture()
def deposited_weighted(safe, balancer, wbtc, weth, staked_bpt):
    bal_before_staked_bpt = staked_bpt.balanceOf(safe)
    assert bal_before_staked_bpt == 0

    underylings = [wbtc, weth]
    amounts = [wbtc.balanceOf(safe), weth.balanceOf(safe)]

    balancer.deposit_and_stake(underylings, amounts)

    assert wbtc.balanceOf(safe) == 0
    assert weth.balanceOf(safe) == 0
    assert staked_bpt.balanceOf(safe) > 0


@pytest.fixture()
def deposited_stable(safe, balancer, dai, threepool_bpt, threepool_staked_bpt):
    bal_before_staked_bpt = threepool_staked_bpt.balanceOf(safe)
    bal_before_dai = dai.balanceOf(safe)

    balancer.deposit_and_stake_single_asset(
        dai,
        dai.balanceOf(safe) / 4,
        threepool_bpt
    )

    assert dai.balanceOf(safe) < bal_before_dai
    assert threepool_staked_bpt.balanceOf(safe) > bal_before_staked_bpt


def test_unstake_and_withdraw_all_weighted(safe, balancer, wbtc, weth, bpt, staked_bpt, deposited_weighted):
    bal_before_weth = weth.balanceOf(safe)
    bal_before_wbtc = wbtc.balanceOf(safe)

    balancer.unstake_all_and_withdraw_all(pool=bpt)

    assert weth.balanceOf(safe) > bal_before_weth
    assert wbtc.balanceOf(safe) > bal_before_wbtc

    assert staked_bpt.balanceOf(safe) == 0
    assert bpt.balanceOf(safe) == 0


def test_unstake_and_withdraw_all_single_asset(safe, balancer, wbtc, bpt, staked_bpt, deposited_weighted):
    bal_before_wbtc = wbtc.balanceOf(safe)

    balancer.unstake_and_withdraw_all_single_asset(wbtc, pool=bpt)

    assert wbtc.balanceOf(safe) > bal_before_wbtc
    assert staked_bpt.balanceOf(safe) == 0
    assert bpt.balanceOf(safe) == 0


def test_unstake_and_withdraw_all_stable(safe, balancer, dai, threepool_bpt, threepool_staked_bpt):
    bal_before_dai = dai.balanceOf(safe)
    
    with pytest.raises(NotImplementedError):
        with brownie.reverts():
            balancer.unstake_and_withdraw_all_single_asset(dai, pool=threepool_bpt)

            assert dai.balanceOf(safe) > bal_before_dai
            assert threepool_staked_bpt.balanceOf(safe) == 0
            assert threepool_bpt.balanceOf(safe) == 0
