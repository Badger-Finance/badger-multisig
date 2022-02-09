import pytest
from great_ape_safe import GreatApeSafe
                            # avoid collision with curve registry fixture
from helpers.addresses import registry as registry_addrs


@pytest.fixture(scope="module", autouse=True)
def shared_setup(module_isolation):
    pass


# Global fixtures
@pytest.fixture
def safe():
    return GreatApeSafe(registry_addrs.eth.badger_wallets.ops_multisig)

@pytest.fixture
def USDC(safe):
    return safe.contract(registry_addrs.eth.treasury_tokens.USDC)

# Aave fixtures
@pytest.fixture
def aave(safe):
    safe.init_aave()
    return safe.aave

@pytest.fixture
def aUSDC(safe):
    return safe.contract(registry_addrs.eth.treasury_tokens.aUSDC)

@pytest.fixture
def sktAAVE(safe):
    return safe.contract(registry_addrs.eth.treasury_tokens.stkAAVE)

@pytest.fixture
def AAVE(safe):
    return safe.contract(registry_addrs.eth.treasury_tokens.AAVE)


# Curve fixtures
@pytest.fixture
def curve(safe):
    safe.init_curve()
    return safe.curve

@pytest.fixture
def registry(safe):
    provider = safe.contract(registry_addrs.eth.curve.provider)
    return safe.contract(provider.get_registry())

@pytest.fixture
def tripool_address(registry):
    return registry.pool_list(0)

@pytest.fixture
def tripool_lptoken(safe, registry):
    tripool = safe.contract(registry.pool_list(0))
    return safe.contract(registry.get_lp_token(tripool))

@pytest.fixture
def threepool_lp(safe):
    return safe.contract(registry_addrs.eth.treasury_tokens.crv3pool)

@pytest.fixture
def CRV(safe):
    return safe.contract(registry_addrs.eth.treasury_tokens.CRV)
    

# Compound Fixtures
@pytest.fixture
def compound(safe):
    safe.init_compound()
    return safe.compound

@pytest.fixture
def cUSDC(safe):
    return safe.contract(registry_addrs.eth.treasury_tokens.cUSDC)

@pytest.fixture
def cETH(safe):
    return safe.contract(registry_addrs.eth.treasury_tokens.cETH)

@pytest.fixture
def COMP(safe):
    return safe.contract(registry_addrs.eth.treasury_tokens.COMP)

# Convex
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