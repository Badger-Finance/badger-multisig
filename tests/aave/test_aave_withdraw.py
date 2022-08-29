import pytest


@pytest.fixture(scope='function', autouse=True)
def deposited(aave, USDC):
    to_deposit = 10_000 * 10**USDC.decimals()
    aave.deposit(USDC, to_deposit)


def test_withdraw(safe, aave, USDC, aUSDC):
    bal_before_usdc = USDC.balanceOf(safe)
    bal_before_ausdc = aUSDC.balanceOf(safe)

    to_withdraw = 1000 * 10**USDC.decimals()

    aave.withdraw(USDC, to_withdraw)

    # aave will sometimes give you slightly more/less than what you asked for, so test >=
    assert USDC.balanceOf(safe) >= bal_before_usdc + to_withdraw
    assert aUSDC.balanceOf(safe) >= bal_before_ausdc - to_withdraw


def test_withdraw_all(safe, aave, USDC, aUSDC):
    bal_before_usdc = USDC.balanceOf(safe)
    bal_before_ausdc = aUSDC.balanceOf(safe)

    aave.withdraw_all(USDC)

    assert USDC.balanceOf(safe) >= bal_before_usdc + bal_before_ausdc
    assert aUSDC.balanceOf(safe) == 0
