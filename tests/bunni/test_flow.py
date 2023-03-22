from brownie import interface, chain
import pytest


@pytest.fixture(scope="function", autouse=True)
def deposited(safe, bunni, badger, wbtc):
    wbtc_amount = 1e8
    badger_amount = 10_000e18

    wbtc_before = wbtc.balanceOf(safe)
    badger_before = badger.balanceOf(safe)

    # https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
    badger.approve(bunni.router, 0)
    badger.approve(bunni.hub, 0)

    assert badger.allowance(safe, bunni.router) == 0
    assert badger.allowance(safe, bunni.hub) == 0

    bunni_token_addr = bunni.deposit(wbtc_amount, badger_amount)

    assert interface.IBunniToken(bunni_token_addr).balanceOf(safe) > 0
    assert wbtc.balanceOf(safe) < wbtc_before
    assert badger.balanceOf(safe) < badger_before


def test_withdraw(safe, bunni, badger, wbtc):
    wbtc_before = wbtc.balanceOf(safe)
    badger_before = badger.balanceOf(safe)

    bunni_token_addr = bunni.hub.getBunniToken(bunni.bunni_key)

    bunni_token = interface.IBunniToken(bunni_token_addr)
    bunni.withdraw()

    assert bunni_token.balanceOf(safe) == 0
    assert wbtc.balanceOf(safe) > wbtc_before
    assert badger.balanceOf(safe) > badger_before
    chain.reset()


def test_stake_and_unstake(safe, bunni):
    bunni_token_addr = bunni.hub.getBunniToken(bunni.bunni_key)
    bunni_token = interface.IBunniToken(bunni_token_addr)

    gauge_addr = bunni.deploy_gauge(1e18)
    gauge = safe.contract(gauge_addr)

    before_bunni = bunni_token.balanceOf(safe)
    before_gauge = gauge.balanceOf(safe)

    bunni.stake(gauge_addr)

    assert bunni_token.balanceOf(safe) < before_bunni
    assert gauge.balanceOf(safe) > before_gauge

    before_bunni = bunni_token.balanceOf(safe)
    before_gauge = gauge.balanceOf(safe)

    bunni.unstake(gauge_addr)

    assert gauge.balanceOf(safe) < before_gauge
    assert bunni_token.balanceOf(safe) > before_bunni


def test_compound(bunni, badger, wbtc):
    badger.approve(bunni.router, 0)

    # simulate some trading so we have some fees to compound
    bunni.swap([badger, wbtc], 1000e18)
    bunni.swap([wbtc, badger], 0.1e8)

    bunni.compound()
