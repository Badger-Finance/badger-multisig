from datetime import datetime

import pytest
from brownie import Contract, accounts, chain
from brownie_tokens import MintableForkToken

from helpers.addresses import registry


@pytest.fixture(scope='module')
def deployer():
    return accounts[0]


@pytest.fixture(scope='module')
def dripper(deployer):
    from scripts.deployment.deploy_rembadger_dripper import main
    return main(deployer)


@pytest.fixture(scope="module")
def badger():
    return MintableForkToken(registry.eth.treasury_tokens.BADGER)


@pytest.fixture(scope='module', autouse=True)
def topup_and_fast_forward(dripper, badger):
    badger._mint_for_testing(dripper, 100_000 * 10**badger.decimals())
    assert badger.balanceOf(dripper) > 0
    now = datetime.now().timestamp()
    delta = dripper.start() - now
    if delta > 0:
        # dripping period still has to start, sleep until then
        chain.sleep(delta + 60 * 60 * 24)


def test_beneficiary(dripper):
    assert dripper.beneficiary() == registry.eth.sett_vaults.remBADGER


def test_timestamps(dripper):
    assert dripper.start() > dripper.duration()


def test_duration(dripper):
    assert dripper.duration() > 0
    assert dripper.start() + dripper.duration() > datetime.now().timestamp(),\
        'dripping period already expired; increase start or duration'


def test_keeper(dripper, deployer):
    assert dripper.keeper() == deployer


def test_release_from_keeper(badger, dripper, deployer):
    bal_before = badger.balanceOf(dripper.beneficiary())
    dripper.release(badger, {'from': deployer})
    assert badger.balanceOf(dripper.beneficiary()) > bal_before


def test_accounting_released(dripper, badger):
    assert dripper.released(badger, {'from': accounts[1]}) > 0


def test_release_from_techops(badger, dripper, techops):
    bal_before = badger.balanceOf(dripper.beneficiary())
    dripper.release(badger, {'from': techops.account})
    assert badger.balanceOf(dripper.beneficiary()) > bal_before


def test_release_from_dev(badger, dripper, dev):
    bal_before = badger.balanceOf(dripper.beneficiary())
    dripper.release(badger, {'from': dev.account})
    assert badger.balanceOf(dripper.beneficiary()) > bal_before


@pytest.mark.xfail
def test_release_from_random(badger, dripper):
    bal_before = badger.balanceOf(dripper.beneficiary())
    dripper.release(badger, {'from': accounts[1]})
    assert badger.balanceOf(dripper.beneficiary()) > bal_before


def test_set_keeper_from_dev(dripper, dev):
    dripper.setKeeper(accounts[1], {'from': dev.account})


def test_set_keeper_from_techops(dripper, techops):
    dripper.setKeeper(accounts[1], {'from': techops.account})


@pytest.mark.xfail
def test_set_keeper_from_random(dripper):
    dripper.setKeeper(accounts[1], {'from': accounts[1]})
