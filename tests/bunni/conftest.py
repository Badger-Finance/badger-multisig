import pytest
from helpers.addresses import r
from brownie import interface
from brownie_tokens import MintableForkToken

RANGE0 = 0.0001000
RANGE1 = 0.0002000


@pytest.fixture
def badger_wbtc_pool(safe):
    return interface.IUniswapV3Pool(r.uniswap.v3pool_wbtc_badger, owner=safe.account)


@pytest.fixture
def bunni(safe, badger_wbtc_pool):
    safe.init_bunni(pool_addr=badger_wbtc_pool.address, range0=RANGE0, range1=RANGE1)
    return safe.bunni


@pytest.fixture
def badger(safe):
    badger = interface.ERC20(r.treasury_tokens.BADGER, owner=safe.account)
    MintableForkToken(badger.address)._mint_for_testing(
        safe, 100_000 * 10 ** badger.decimals()
    )
    return badger


@pytest.fixture
def wbtc(safe):
    wbtc = interface.IWBTC(r.treasury_tokens.WBTC, owner=safe.account)
    MintableForkToken(wbtc.address, owner=safe.account)._mint_for_testing(
        safe, 10 * 10 ** wbtc.decimals()
    )
    return wbtc


@pytest.fixture
def weth(safe):
    weth = interface.ERC20(r.treasury_tokens.WETH, owner=safe.account)
    MintableForkToken(weth.address)._mint_for_testing(safe, 10 * 10 ** 18)
    return weth


@pytest.fixture
def aura(safe):
    aura = interface.ERC20(r.treasury_tokens.AURA, owner=safe.account)
    MintableForkToken(aura.address)._mint_for_testing(safe, 1000 * 10 ** 18)
    return aura


@pytest.fixture
def weth_aura_pool(safe):
    return interface.IUniswapV3Pool(
        "0x4Be410e2fF6a5F1718ADA572AFA9E8D26537242b", owner=safe.account
    )


@pytest.fixture
def weth_aura_bunni_token(safe):
    return safe.contract("0x30d789c93aAB4E70a307e546ca3265B0a6572E64")


@pytest.fixture
def weth_aura_gauge(safe):
    return safe.contract("0x13A227b851ed1274e205535b3CF1daF6e2bA1E5a")
