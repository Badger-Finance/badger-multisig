import pytest
from brownie import interface
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
    threepool = interface.ICurveLP(registry_addr.eth.treasury_tokens.crv3pool, owner=safe.account)
    threepool_mintable = MintableForkToken(
        threepool.address, owner=safe.account
    )
    threepool_mintable._mint_for_testing(safe, 100_000 * 10**threepool.decimals())
    return threepool


@pytest.fixture
def threepool_lp(safe):
    return safe.contract(registry_addr.eth.treasury_tokens.crv3pool)


@pytest.fixture
def CRV(safe):
    crv = interface.ERC20(registry_addr.eth.treasury_tokens.CRV, owner=safe.account)
    crv_mintable = MintableForkToken(
        crv.address, owner=safe.account
    )
    crv_mintable._mint_for_testing(safe, 100 * 10**crv.decimals())
    return crv


@pytest.fixture
def cvxCRV(safe):
    cvxcrv = interface.ICurveLP(registry_addr.eth.treasury_tokens.cvxCRV)
    cvxcrv_mintable = MintableForkToken(
        cvxcrv.address, owner=safe.account
    )
    cvxcrv_mintable._mint_for_testing(safe, 100 * 10**cvxcrv.decimals())
    return cvxcrv


@pytest.fixture
def dai(safe):
    dai = interface.ERC20(registry_addr.eth.treasury_tokens.DAI, owner=safe.account)
    dai_mintable = MintableForkToken(
        dai.address, owner=safe.account
    )
    dai_mintable._mint_for_testing(safe, 1_000_000 * 10**dai.decimals())
    return dai
