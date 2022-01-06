import pytest


@pytest.fixture(scope='function', autouse=True)
def deposited(compound, USDC):
    to_deposit_usdc = 100_000 * 10**USDC.decimals()
    compound.deposit(USDC, to_deposit_usdc)

    to_deposit_eth = 10**18
    compound.deposit_eth(to_deposit_eth)


def test_withdraw(safe, compound, USDC, cUSDC):

    before_bal_usdc = USDC.balanceOf(safe)
    before_bal_cUSDC = cUSDC.balanceOf(safe)
    to_withdraw = 100_000 * 10**USDC.decimals()

    compound.withdraw(USDC, to_withdraw)

    assert USDC.balanceOf(safe) == before_bal_usdc + to_withdraw
    # Can be more precise by calculating Ctokens exchange rates
    assert cUSDC.balanceOf(safe) < before_bal_cUSDC


def test_withdraw_eth(safe, compound, cETH):

    before_bal_eth= safe.account.balance()
    before_bal_ceth = cETH.balanceOf(safe)

    to_withdraw = 10**18

    compound.withdraw_eth(to_withdraw)

    assert safe.account.balance() == before_bal_eth + to_withdraw
    assert cETH.balanceOf(safe) < before_bal_ceth

def test_withdraw_ctoken(safe, compound, USDC, cUSDC):
    before_bal_usdc = USDC.balanceOf(safe)

    to_withdraw = cUSDC.balanceOf(safe)

    compound.withdraw_ctoken(cUSDC, to_withdraw)

    assert USDC.balanceOf(safe) > before_bal_usdc
    assert cUSDC.balanceOf(safe) == 0
