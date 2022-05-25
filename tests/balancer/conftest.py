import pytest
from brownie import Contract
from brownie_tokens import MintableForkToken
from helpers.addresses import registry


@pytest.fixture
def balancer(dev):
    dev.init_balancer()
    return dev.balancer


@pytest.fixture
def bpt(dev):
    return dev.contract(registry.eth.balancer.B_50_BTC_50_WETH)


@pytest.fixture
def staked_bpt(dev, balancer, bpt):
    gauge_factory = balancer.gauge_factory
    return dev.contract(gauge_factory.getPoolGauge(bpt))


@pytest.fixture
def threepool_bpt(dev):
    return dev.contract("0x06Df3b2bbB68adc8B0e302443692037ED9f91b42")


@pytest.fixture
def threepool_staked_bpt(dev, balancer, threepool_bpt):
    gauge_factory = balancer.gauge_factory
    return dev.contract(gauge_factory.getPoolGauge(threepool_bpt))


@pytest.fixture
def weighted_bpt(dev):
    # 60 weth/40 dai
    return dev.contract('0x0b09deA16768f0799065C475bE02919503cB2a35')


@pytest.fixture
def lido_bpt(dev):
    return dev.contract("0x32296969Ef14EB0c6d29669C550D4a0449130230")


@pytest.fixture
def lido_staked_bpt(dev, balancer, lido_bpt):
    gauge_factory = balancer.gauge_factory
    return dev.contract(gauge_factory.getPoolGauge(lido_bpt))


@pytest.fixture
def weighted_staked_bpt(dev, balancer, weighted_bpt):
    gauge_factory = balancer.gauge_factory
    return dev.contract(gauge_factory.getPoolGauge(weighted_bpt))


@pytest.fixture
def badger_bpt(dev):
    return dev.contract(registry.eth.balancer.B_20_BTC_80_BADGER)


@pytest.fixture
def badger_staked_bpt(dev, balancer, badger_bpt):
    gauge_factory = balancer.gauge_factory
    return dev.contract(gauge_factory.getPoolGauge(badger_bpt))


@pytest.fixture
def ldo(dev):
    return dev.contract("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32")


@pytest.fixture
def bal(dev):
    Contract.from_explorer(registry.eth.treasury_tokens.BAL)
    bal = MintableForkToken(
        registry.eth.treasury_tokens.BAL, owner=dev.account
    )
    bal._mint_for_testing(dev, 10 * 10**bal.decimals())
    return Contract(
        registry.eth.treasury_tokens.BAL, owner=dev.account
    )


@pytest.fixture
def wbtc(dev):
    Contract.from_explorer(registry.eth.treasury_tokens.WBTC)
    wbtc = MintableForkToken(
        registry.eth.treasury_tokens.WBTC, owner=dev.account
    )
    wbtc._mint_for_testing(dev, 10 * 10**wbtc.decimals())
    return Contract(
        registry.eth.treasury_tokens.WBTC, owner=dev.account
    )


@pytest.fixture
def weth(dev):
    Contract.from_explorer(registry.eth.treasury_tokens.WETH)
    weth = MintableForkToken(
        registry.eth.treasury_tokens.WETH, owner=dev.account
    )
    weth._mint_for_testing(dev, 100 * 10**weth.decimals())
    return Contract(
        registry.eth.treasury_tokens.WETH, owner=dev.account
    )

@pytest.fixture
def dai(dev):
    Contract.from_explorer(registry.eth.treasury_tokens.DAI)
    dai = MintableForkToken(
        registry.eth.treasury_tokens.DAI, owner=dev.account
    )
    dai._mint_for_testing(dev, 10_000 * 10**dai.decimals())
    return Contract(
        registry.eth.treasury_tokens.DAI, owner=dev.account
    )


@pytest.fixture
def badger(dev):
    Contract.from_explorer(registry.eth.treasury_tokens.BADGER)
    badger = MintableForkToken(
        registry.eth.treasury_tokens.BADGER
    )
    badger._mint_for_testing(dev, 100_000 * 10**badger.decimals())
    return Contract(
        registry.eth.treasury_tokens.BADGER, owner=dev.account
    )
