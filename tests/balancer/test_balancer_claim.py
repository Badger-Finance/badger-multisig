import pytest
from brownie import chain


@pytest.fixture(autouse=True)
def deposited(dev, balancer, weth, lido_bpt, lido_staked_bpt):
    bal_before_staked_bpt = lido_staked_bpt.balanceOf(dev)
    assert bal_before_staked_bpt == 0

    balancer.deposit_and_stake_single_asset(weth, weth.balanceOf(dev), lido_bpt)

    assert weth.balanceOf(dev) == 0
    assert lido_staked_bpt.balanceOf(dev) > 0


def test_claim_all(dev, balancer, lido_bpt, ldo):
    bal_before_ldo = ldo.balanceOf(dev)

    chain.sleep(100)
    chain.mine(100)

    balancer.claim_all(pool=lido_bpt)

    assert ldo.balanceOf(dev) > bal_before_ldo
