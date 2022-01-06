import pytest
from great_ape_safe import GreatApeSafe


@pytest.fixture(scope="module", autouse=True)
def shared_setup(module_isolation):
    pass


# Global fixtures
@pytest.fixture
def safe():
    return GreatApeSafe('dev.badgerdao.eth')

@pytest.fixture
def USDC(safe):
    return safe.contract('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48')

# Aave fixtures
@pytest.fixture
def aave(safe):
    safe.init_aave()
    return safe.aave

@pytest.fixture
def aUSDC(safe):
    return safe.contract('0xBcca60bB61934080951369a648Fb03DF4F96263C')

@pytest.fixture
def sktAAVE(safe):
    return safe.contract('0x4da27a545c0c5B758a6BA100e3a049001de870f5')

@pytest.fixture
def AAVE(safe):
    return safe.contract('0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9')


# Curve fixtures
@pytest.fixture
def curve(safe):
    safe.init_curve()
    return safe.curve

@pytest.fixture
def registry(safe):
    provider = safe.contract('0x0000000022D53366457F9d5E68Ec105046FC4383')
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
    return safe.contract('0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490')

@pytest.fixture
def CRV(safe):
    return safe.contract('0xD533a949740bb3306d119CC777fa900bA034cd52')
    

# Compound Fixtures
@pytest.fixture
def compound(safe):
    safe.init_compound()
    return safe.compound

@pytest.fixture
def cUSDC(safe):
    return safe.contract('0x39AA39c021dfbaE8faC545936693aC917d5E7563')

@pytest.fixture
def cETH(safe):
    return safe.contract('0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5')

@pytest.fixture
def COMP(safe):
    return safe.contract('0xc00e94Cb662C3520282E6f5717214004A7f26888')

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