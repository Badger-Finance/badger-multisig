import pytest
from brownie import Contract
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
    return safe.contract('0x0b09deA16768f0799065C475bE02919503cB2a35')


@pytest.fixture
def weighted_staked_bpt(safe, balancer, weighted_bpt):
    gauge_factory = balancer.gauge_factory
    return safe.contract(gauge_factory.getPoolGauge(weighted_bpt))


@pytest.fixture
def badger_bpt(safe):
    return safe.contract(registry.eth.balancer.B_20_BTC_80_BADGER)


@pytest.fixture
def badger_staked_bpt(safe, balancer, badger_bpt):
    gauge_factory = balancer.gauge_factory
    return safe.contract(gauge_factory.getPoolGauge(badger_bpt))


@pytest.fixture
def bal(safe, vault):
    Contract.from_explorer(registry.eth.treasury_tokens.BAL)
    bal = MintableForkToken(
        registry.eth.treasury_tokens.BAL, owner=safe.account
    )
    bal._mint_for_testing(safe, 1000 * 10**bal.decimals())
    bal._mint_for_testing(vault, 1000 * 10**bal.decimals())

    return Contract(
        registry.eth.treasury_tokens.BAL, owner=safe.account
    )


@pytest.fixture
def wbtc(safe):
    Contract.from_explorer(registry.eth.treasury_tokens.WBTC)
    wbtc = MintableForkToken(
        registry.eth.treasury_tokens.WBTC, owner=safe.account
    )
    wbtc._mint_for_testing(safe, 10 * 10**wbtc.decimals())
    return Contract(
        registry.eth.treasury_tokens.WBTC, owner=safe.account
    )


@pytest.fixture
def weth(safe):
    Contract.from_explorer(registry.eth.treasury_tokens.WETH)
    weth = MintableForkToken(
        registry.eth.treasury_tokens.WETH, owner=safe.account
    )
    weth._mint_for_testing(safe, 100 * 10**weth.decimals())
    return Contract(
        registry.eth.treasury_tokens.WETH, owner=safe.account
    )


@pytest.fixture
def badger(safe):
    Contract.from_explorer(registry.eth.treasury_tokens.BADGER)
    badger = MintableForkToken(
        registry.eth.treasury_tokens.BADGER
    )
    badger._mint_for_testing(safe, 100_000 * 10**badger.decimals())
    return Contract(
        registry.eth.treasury_tokens.BADGER, owner=safe.account
    )


@pytest.fixture
def dai(safe):
    Contract.from_explorer(registry.eth.treasury_tokens.DAI)
    dai = MintableForkToken(
        registry.eth.treasury_tokens.DAI, owner=safe.account
    )
    dai._mint_for_testing(safe, 1_000_000 * 10**dai.decimals())
    return Contract(
        registry.eth.treasury_tokens.DAI, owner=safe.account
    )
