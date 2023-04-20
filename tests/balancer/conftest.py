import pytest
from brownie import interface
from brownie_tokens import MintableForkToken
from helpers.addresses import registry


@pytest.fixture
def balancer(safe):
    safe.init_balancer()
    return safe.balancer


@pytest.fixture
def bpt(safe):
    return safe.contract(registry.eth.balancer.B_50_BTC_50_WETH)


@pytest.fixture
def staked_bpt(safe, balancer, bpt):
    gauge_factory = balancer.gauge_factory
    return safe.contract(gauge_factory.getPoolGauge(bpt))


@pytest.fixture
def threepool_bpt(safe):
    return safe.contract("0x06Df3b2bbB68adc8B0e302443692037ED9f91b42")


@pytest.fixture
def threepool_staked_bpt(safe, balancer, threepool_bpt):
    gauge_factory = balancer.gauge_factory
    return safe.contract(gauge_factory.getPoolGauge(threepool_bpt))


@pytest.fixture
def weighted_bpt(safe):
    # 60 weth/40 dai
    return safe.contract("0x0b09deA16768f0799065C475bE02919503cB2a35")


@pytest.fixture
def weighted_staked_bpt(safe, balancer, weighted_bpt):
    gauge_factory = balancer.gauge_factory
    return safe.contract(gauge_factory.getPoolGauge(weighted_bpt))


@pytest.fixture
def badger_bpt(safe):
    return safe.contract(registry.eth.balancer.B_20_BTC_80_BADGER)


@pytest.fixture
def badger_staked_bpt(safe, balancer, badger_bpt):
    return safe.contract(balancer.get_preferential_gauge(badger_bpt))


@pytest.fixture
def bal(safe, vault):
    bal = interface.ERC20(registry.eth.treasury_tokens.BAL, owner=safe.account)
    bal_mintable = MintableForkToken(bal.address, owner=safe.account)
    bal_mintable._mint_for_testing(safe, 1000 * 10 ** bal.decimals())
    bal_mintable._mint_for_testing(vault, 1000 * 10 ** bal.decimals())
    return bal


@pytest.fixture
def wbtc(safe):
    wbtc = interface.IWBTC(registry.eth.treasury_tokens.WBTC, owner=safe.account)
    wbtc_mintable = MintableForkToken(wbtc.address, owner=safe.account)
    wbtc_mintable._mint_for_testing(safe, 10 * 10 ** wbtc.decimals())
    return wbtc


@pytest.fixture
def weth(safe):
    weth = interface.IWETH9(registry.eth.treasury_tokens.WETH, owner=safe.account)
    weth_mintable = MintableForkToken(weth.address, owner=safe.account)
    weth_mintable._mint_for_testing(safe, 100 * 10 ** weth.decimals())
    return weth


@pytest.fixture
def badger(safe):
    badger = interface.ERC20(registry.eth.treasury_tokens.BADGER, owner=safe.account)
    badger_mintable = MintableForkToken(badger.address)
    badger_mintable._mint_for_testing(safe, 100_000 * 10 ** badger.decimals())
    return badger


@pytest.fixture
def usdt(safe):
    usdt = interface.ITetherToken(registry.eth.treasury_tokens.USDT, owner=safe.account)
    usdt_mintable = MintableForkToken(usdt.address, owner=safe.account)
    usdt_mintable._mint_for_testing(safe, 1000 * 10 ** usdt.decimals())
    return usdt
