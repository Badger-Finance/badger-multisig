import pytest
from brownie import chain


@pytest.fixture(scope="function", autouse=True)
def deposited(aave, USDC):
    to_deposit = 10_000 * 10**USDC.decimals()
    aave.deposit(USDC, to_deposit)

def test_claim(safe, aave, sktAAVE):
    before_bal_sktaave = sktAAVE.balanceOf(safe)
    chain.sleep(1000)
    chain.mine()
    aave.claim_all()

    assert sktAAVE.balanceOf(safe) > before_bal_sktaave

def test_unstake_and_claim(safe, aave, sktAAVE, AAVE):
    before_bal_aave = AAVE.balanceOf(safe)
    
    # Start staking vesting period
    sktAAVE.cooldown()
    wait_peroid = sktAAVE.COOLDOWN_SECONDS()

    # Fast forward to end of vesting period
    chain.sleep(wait_peroid + 1)
    chain.mine()

    aave.unstake_and_claim_all()

    assert AAVE.balanceOf(safe) > before_bal_aave