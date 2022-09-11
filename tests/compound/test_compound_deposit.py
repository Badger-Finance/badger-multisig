def test_deposit(safe, compound, USDC, cUSDC):
    before_bal_usdc = USDC.balanceOf(safe)
    before_bal_cUSDC = cUSDC.balanceOf(safe)
    to_deposit = 100_000 * 10 ** USDC.decimals()

    compound.deposit(USDC, to_deposit)

    assert USDC.balanceOf(safe) == before_bal_usdc - to_deposit

    # Can be more precise by calculating Ctokens exchange rates
    assert cUSDC.balanceOf(safe) > before_bal_cUSDC


def test_deposit_eth(safe, compound, cETH):
    before_bal_ceth = cETH.balanceOf(safe)
    before_bal_eth = safe.account.balance()

    to_deposit = 10**18

    compound.deposit_eth(to_deposit)

    assert safe.account.balance() == before_bal_eth - to_deposit
    assert cETH.balanceOf(safe) > before_bal_ceth
