import pytest
from helpers.addresses import registry


@pytest.fixture
def aave(safe):
    safe.init_aave()
    return safe.aave


@pytest.fixture
def aUSDC(safe):
    return safe.contract(registry.eth.treasury_tokens.aUSDC)


@pytest.fixture
def sktAAVE(safe):
    return safe.contract(registry.eth.treasury_tokens.stkAAVE)


@pytest.fixture
def AAVE(safe):
    return safe.contract(registry.eth.treasury_tokens.AAVE)
