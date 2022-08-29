import pytest
from brownie import Contract
from brownie_tokens import MintableForkToken
from helpers.addresses import registry as registry_addr


@pytest.fixture
def curve(safe):
    safe.init_curve()
    return safe.curve


@pytest.fixture
def registry(safe):
    provider = safe.contract(registry_addr.eth.curve.provider)
    return safe.contract(provider.get_registry())


@pytest.fixture
def threepool_lptoken(safe):
    Contract.from_explorer(registry_addr.eth.treasury_tokens.crv3pool)
    threepool = MintableForkToken(
        registry_addr.eth.treasury_tokens.crv3pool, owner=safe.account
    )
    threepool._mint_for_testing(safe, 100_000 * 10**threepool.decimals())
    return Contract(
        registry_addr.eth.treasury_tokens.crv3pool, owner=safe.account
    )


@pytest.fixture
def threepool_lp(safe):
    return safe.contract(registry_addr.eth.treasury_tokens.crv3pool)


@pytest.fixture
def CRV(safe):
    Contract.from_explorer(registry_addr.eth.treasury_tokens.CRV)
    crv = MintableForkToken(
        registry_addr.eth.treasury_tokens.CRV, owner=safe.account
    )
    crv._mint_for_testing(safe, 100 * 10**crv.decimals())
    return Contract(
        registry_addr.eth.treasury_tokens.CRV, owner=safe.account
    )


@pytest.fixture
def cvxCRV(safe):
    Contract.from_explorer(registry_addr.eth.treasury_tokens.cvxCRV)
    cvxcrv = MintableForkToken(
        registry_addr.eth.treasury_tokens.cvxCRV, owner=safe.account
    )
    cvxcrv._mint_for_testing(safe, 100 * 10**cvxcrv.decimals())
    return Contract(
        registry_addr.eth.treasury_tokens.cvxCRV, owner=safe.account
    )


@pytest.fixture
def dai(safe):
    Contract.from_explorer(registry_addr.eth.treasury_tokens.DAI)
    dai = MintableForkToken(
        registry_addr.eth.treasury_tokens.DAI, owner=safe.account
    )
    dai._mint_for_testing(safe, 1_000_000 * 10**dai.decimals())
    return Contract(
        registry_addr.eth.treasury_tokens.DAI, owner=safe.account
    )
