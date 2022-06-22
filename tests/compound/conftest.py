import pytest
from helpers.addresses import registry


@pytest.fixture
def compound(safe):
    safe.init_compound()
    return safe.compound


@pytest.fixture
def cUSDC(safe):
    return safe.contract(registry.eth.treasury_tokens.cUSDC)


@pytest.fixture
def cETH(safe):
    return safe.contract(registry.eth.treasury_tokens.cETH)


@pytest.fixture
def COMP(safe):
    return safe.contract(registry.eth.treasury_tokens.COMP)
