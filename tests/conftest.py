import pytest
from brownie import Contract
from brownie_tokens import MintableForkToken

from great_ape_safe import GreatApeSafe
# avoid collision with curve registry fixture
from helpers.addresses import registry as registry_addr


@pytest.fixture(scope="module", autouse=True)
def shared_setup(module_isolation):
    pass


# global fixtures
@pytest.fixture
def safe():
    return GreatApeSafe(registry_addr.eth.badger_wallets.ops_multisig)


@pytest.fixture
def dev():
    return GreatApeSafe(registry_addr.eth.badger_wallets.dev_multisig)


@pytest.fixture
def USDC(safe):
    Contract.from_explorer(registry_addr.eth.treasury_tokens.USDC)
    usdc = MintableForkToken(
        registry_addr.eth.treasury_tokens.USDC, owner=safe.account
    )
    usdc._mint_for_testing(safe, 100_000 * 10**usdc.decimals())
    return Contract(
        registry_addr.eth.treasury_tokens.USDC, owner=safe.account
    )


@pytest.fixture
def dai(safe):
    Contract.from_explorer(registry_addr.eth.treasury_tokens.DAI)
    dai = MintableForkToken(
        registry_addr.eth.treasury_tokens.DAI, owner=safe.account
    )
    dai._mint_for_testing(safe, 100_000 * 10**dai.decimals())
    return Contract(
        registry_addr.eth.treasury_tokens.DAI, owner=safe.account
    )


# aave fixtures
@pytest.fixture
def aave(safe):
    safe.init_aave()
    return safe.aave


@pytest.fixture
def aUSDC(safe):
    return safe.contract(registry_addr.eth.treasury_tokens.aUSDC)



@pytest.fixture
def sktAAVE(safe):
    return safe.contract(registry_addr.eth.treasury_tokens.stkAAVE)



@pytest.fixture
def AAVE(safe):
    return safe.contract(registry_addr.eth.treasury_tokens.AAVE)


# curve fixtures
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


# compound fixtures
@pytest.fixture
def compound(safe):
    safe.init_compound()
    return safe.compound


@pytest.fixture
def cUSDC(safe):
    return safe.contract(registry_addr.eth.treasury_tokens.cUSDC)



@pytest.fixture
def cETH(safe):
    return safe.contract(registry_addr.eth.treasury_tokens.cETH)



@pytest.fixture
def COMP(safe):
    return safe.contract(registry_addr.eth.treasury_tokens.COMP)


# convex fixtures
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


# rari fixtures
@pytest.fixture
def rari(dev):
    dev.init_rari()
    return dev.rari
