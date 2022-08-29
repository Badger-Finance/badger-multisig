import pytest
from brownie import chain


@pytest.fixture(scope='function', autouse=True)
def deposited(compound, USDC):
    to_deposit_usdc = 10_000 * 10**USDC.decimals()
    compound.deposit(USDC, to_deposit_usdc)

    to_deposit_eth = 10**18
    compound.deposit_eth(to_deposit_eth)

def test_claim_all(safe, compound, COMP):
    bal_before_comp = COMP.balanceOf(safe)
    chain.sleep(100)
    chain.mine()

    compound.claim_all()

    assert COMP.balanceOf(safe) > bal_before_comp

def test_claim_underlying(safe, compound, COMP, USDC):
    bal_before_comp = COMP.balanceOf(safe)

    # Fast foward chain ensure rewards are available
    chain.sleep(100)
    chain.mine()

    compound.claim(USDC)

    assert COMP.balanceOf(safe) > bal_before_comp
