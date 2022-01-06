

def test_deposit(safe, aave, USDC, aUSDC):

    bal_before_usdc = USDC.balanceOf(safe)
    bal_before_ausdc = aUSDC.balanceOf(safe)
    to_deposit = 100_000 * 10**USDC.decimals()

    aave.deposit(USDC, to_deposit)

    assert USDC.balanceOf(safe) == bal_before_usdc - to_deposit
    assert aUSDC.balanceOf(safe) >= bal_before_ausdc + to_deposit
