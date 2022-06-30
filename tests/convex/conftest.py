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
def threepool_lp(safe):
    return safe.contract(registry_addr.eth.treasury_tokens.crv3pool)


@pytest.fixture
def convex(safe):
    safe.init_convex()
    return safe.convex


@pytest.fixture
def convex_rewards(safe, convex, threepool_lp):
    (_,_,_,rewards ) = convex.get_pool_info(threepool_lp)
    return safe.contract(rewards)


@pytest.fixture
def convex_threepool_lp(safe, convex, threepool_lp):
    (_,token,_,_ ) = convex.get_pool_info(threepool_lp)
    return safe.contract(token)


@pytest.fixture
def convex_threepool_reward(safe, convex, threepool_lp):
    (_,_,_,rewards ) = convex.get_pool_info(threepool_lp)
    reward = safe.contract(rewards).rewardToken()
    return safe.contract(reward)
