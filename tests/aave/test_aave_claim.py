import pytest
from brownie import chain


@pytest.fixture(scope="function", autouse=True)
def deposited(aave, USDC):
    to_deposit = 10_000 * 10**USDC.decimals()
    aave.deposit(USDC, to_deposit)


@pytest.mark.skip(reason="no liquidity mining rewards to claim")
def test_claim(safe, aave, stkAAVE):
    before_bal_stkAAVE = stkAAVE.balanceOf(safe)
    chain.sleep(1000)
    chain.mine()
    aave.claim_all()

    assert stkAAVE.balanceOf(safe) > before_bal_stkAAVE


def test_unstake_and_claim(safe, aave, stkAAVE, AAVE):
    before_bal_aave = AAVE.balanceOf(safe)
    
    # Start staking vesting period
    stkAAVE.cooldown()
    wait_peroid = stkAAVE.COOLDOWN_SECONDS()

    # Fast forward to end of vesting period
    chain.sleep(wait_peroid + 1)
    chain.mine()

    aave.unstake_and_claim_all()

    assert AAVE.balanceOf(safe) > before_bal_aave