def test_stable_swap(safe, curve, dai, USDC):
    amount = 10_000 * 10 ** USDC.decimals()

    bal_before_usdc = USDC.balanceOf(safe)
    bal_before_dai = dai.balanceOf(safe)

    curve.swap(USDC, dai, amount)

    assert USDC.balanceOf(safe) == bal_before_usdc - amount
    assert dai.balanceOf(safe) > bal_before_dai


def test_factory_swap(safe, curve, CRV, cvxCRV):
    amount = 100 * 10 ** CRV.decimals()

    bal_before_crv = CRV.balanceOf(safe)
    bal_before_cvxcrv = cvxCRV.balanceOf(safe)

    curve.swap(CRV, cvxCRV, amount)

    assert CRV.balanceOf(safe) == bal_before_crv - amount
    assert cvxCRV.balanceOf(safe) > bal_before_cvxcrv
