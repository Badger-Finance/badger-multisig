import pytest
from helpers.addresses import registry
from brownie import Contract, interface
from brownie_tokens import MintableForkToken


@pytest.fixture
def aave(safe):
    safe.init_aave()
    return safe.aave


@pytest.fixture
def aUSDC(safe):
    return safe.contract(registry.eth.treasury_tokens.aUSDC)


@pytest.fixture
def AAVE(safe):
    return safe.contract(registry.eth.treasury_tokens.AAVE)


@pytest.fixture
def stkAAVE(safe):
    sktaave = interface.IStakedTokenV2Rev3(registry.eth.treasury_tokens.stkAAVE, owner=safe.account)
    sktaave_mintable = MintableForkToken(
        sktaave.address, owner=safe.account
    )
    sktaave_mintable._mint_for_testing(safe, 1000 * 10**sktaave.decimals())
    return sktaave
