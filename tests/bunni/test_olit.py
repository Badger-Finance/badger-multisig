# test claiming/exercising of olit from an active gauge
def test_claim_and_exercise(
    safe, bunni, weth_aura_gauge, weth_aura_bunni_token, weth, aura
):
    bunni.set_bunni_key(weth_aura_bunni_token.address)
    before = bunni.olit.balanceOf(safe)

    bunni.deposit(10e18, 1000e18)
    bunni.stake(weth_aura_gauge.address)
    bunni.claim_rewards(weth_aura_gauge.address)

    assert bunni.olit.balanceOf(safe) > before

    lit_before = bunni.lit.balanceOf(safe)
    olit_before = bunni.olit.balanceOf(safe)
    weth_before = weth.balanceOf(safe)

    bunni.exercise_olit()

    assert bunni.lit.balanceOf(safe) == lit_before + olit_before
    assert bunni.olit.balanceOf(safe) == 0
    assert weth.balanceOf(safe) < weth_before
