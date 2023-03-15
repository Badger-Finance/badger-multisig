def test_swap(safe, balancer, badger, wbtc):
    bal_before_badger = badger.balanceOf(safe)
    bal_before_wbtc = wbtc.balanceOf(safe)

    balancer.swap(badger, wbtc, badger.balanceOf(safe))

    assert wbtc.balanceOf(safe) > bal_before_wbtc
    assert badger.balanceOf(safe) < bal_before_badger
