def test_deposit_and_stake(safe, balancer, wbtc, badger, badger_bpt, badger_staked_bpt):
    bal_before_staked_bpt = badger_staked_bpt.balanceOf(safe)
    bal_before_wbtc = wbtc.balanceOf(safe)
    bal_before_badger = badger.balanceOf(safe)

    ratio = badger_bpt.getNormalizedWeights()[0] / badger_bpt.getNormalizedWeights()[1]
    wbtc_to_deposit = int(3e8)
    badger_to_deposit = int(
        safe.balancer.get_amount_out(wbtc, badger, 1000)
        / 1000
        * wbtc_to_deposit
        / 0.997
        / ratio
    )

    underlyings = [wbtc, badger]
    amounts = [wbtc_to_deposit, badger_to_deposit]

    balancer.deposit_and_stake(underlyings, amounts)

    assert wbtc.balanceOf(safe) == bal_before_wbtc - wbtc_to_deposit
    assert badger.balanceOf(safe) == bal_before_badger - badger_to_deposit
    assert badger_staked_bpt.balanceOf(safe) > bal_before_staked_bpt


def test_unstake_and_withdraw_all(
    safe, balancer, wbtc, badger, badger_bpt, badger_staked_bpt
):
    bal_before_wbtc = wbtc.balanceOf(safe)
    bal_before_badger = badger.balanceOf(safe)

    balancer.unstake_all_and_withdraw_all(pool=badger_bpt)

    assert wbtc.balanceOf(safe) > bal_before_wbtc
    assert badger.balanceOf(safe) > bal_before_badger
    assert badger_staked_bpt.balanceOf(safe) == 0
