import pytest
from brownie import chain


def test_swap(dev, balancer, badger, wbtc):
    bal_before_badger = badger.balanceOf(dev)
    bal_before_wbtc = wbtc.balanceOf(dev)

    balancer.swap(badger, wbtc, badger.balanceOf(dev))

    assert wbtc.balanceOf(dev) > bal_before_wbtc
    assert badger.balanceOf(dev) < bal_before_badger
