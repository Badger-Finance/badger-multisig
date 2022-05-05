from datetime import datetime

import brownie
import pytest
from brownie import accounts, chain
from brownie_tokens import MintableForkToken

from helpers.addresses import registry


@pytest.fixture(scope='module')
def deployer():
    return accounts[0]


@pytest.fixture(scope='module')
def dripper():
    from scripts.deployment.deploy_autonomous_dripper import main
    return main()


@pytest.fixture(scope="module")
def badger():
    return MintableForkToken(registry.eth.treasury_tokens.BADGER)


@pytest.fixture(scope='module', autouse=True)
def topup_and_fast_forward(dripper, badger):
    accounts[1].transfer(dripper, 1e18)
    badger._mint_for_testing(dripper, 100_000 * 10**badger.decimals())
    assert badger.balanceOf(dripper) > 0
    now = datetime.now().timestamp()
    delta = dripper.start() + dripper.interval() - now
    if delta > 0:
        # dripping period still has to start, sleep until next block
        chain.sleep(delta + 1)


def test_timestamps(dripper):
    assert dripper.start() > dripper.duration()


def test_duration(dripper):
    assert dripper.duration() > 0
    assert dripper.start() + dripper.duration() > datetime.now().timestamp(),\
        'dripping period already expired; increase start or duration'


def test_release_from_admin(badger, dripper):
    admin = dripper.admin()
    bal_before = badger.balanceOf(dripper.beneficiary())
    dripper.release(badger, {'from': admin})
    assert badger.balanceOf(dripper.beneficiary()) > bal_before


def test_accounting_released(dripper, badger):
    assert dripper.released(badger, {'from': accounts[1]}) > 0


def test_release_from_random(badger, dripper):
    # add some time to build up releasable funds again
    chain.sleep(60)
    bal_before = badger.balanceOf(dripper.beneficiary())
    dripper.release(badger, {'from': accounts[1]})
    assert badger.balanceOf(dripper.beneficiary()) > bal_before


def test_upkeep_needed(dripper, badger):
    assert chain.time() - dripper.start() > dripper.interval()
    assert badger.balanceOf(dripper) > 0
    upkeep_needed, assets_encoded = dripper.checkUpkeep(b'')
    assert upkeep_needed
    return upkeep_needed, assets_encoded


def test_perform_upkeep(dripper, badger):
    bal_dripper_before = badger.balanceOf(dripper.beneficiary())
    bal_benef_before = badger.balanceOf(dripper)
    upkeep_needed, assets_encoded = test_upkeep_needed(dripper, badger)
    assert upkeep_needed
    dripper.performUpkeep(assets_encoded)
    assert bal_dripper_before > badger.balanceOf(dripper)
    assert badger.balanceOf(dripper.beneficiary()) > bal_benef_before


def test_sweep_eth_from_admin(dripper):
    admin = accounts.at(dripper.admin())
    bal_before = admin.balance()
    dripper.sweep({'from': admin})
    assert admin.balance() > bal_before
    assert dripper.balance() == 0


def test_sweep_eth_from_random(dripper):
    with brownie.reverts():
        dripper.sweep({'from': accounts[1]})


def test_sweep_erc_from_admin(dripper, badger):
    admin = dripper.admin()
    bal_before = badger.balanceOf(admin)
    dripper.sweep(badger, {'from': admin})
    assert badger.balanceOf(admin) > bal_before
    assert badger.balanceOf(dripper) == 0


def test_sweep_erc_from_random(dripper, badger):
    with brownie.reverts():
        dripper.sweep(badger, {'from': accounts[1]})


def test_upkeep_not_needed(dripper, badger):
    assert chain.time() - dripper.start() > dripper.interval()
    assert badger.balanceOf(dripper) == 0
    upkeep_needed, _ = dripper.checkUpkeep(b'')
    assert not upkeep_needed
