from datetime import datetime

import brownie
import pytest
from brownie import accounts, chain, interface
from brownie_tokens import MintableForkToken

from helpers.addresses import registry


@pytest.fixture(scope="module")
def deployer():
    return accounts[0]


@pytest.fixture(scope="module")
def dripper():
    from scripts.deployment.deploy_autonomous_dripper import main

    return main()


@pytest.fixture(scope="module")
def keeper(dripper):
    return interface.IKeeperRegistry(dripper.getKeeperRegistryAddress())


@pytest.fixture(scope="module")
def owner(dripper):
    return accounts.at(dripper.owner(), force=True)


@pytest.fixture(scope="module")
def badger():
    return MintableForkToken(registry.eth.treasury_tokens.BADGER)


@pytest.fixture(scope="module")
def digg():
    return MintableForkToken(registry.eth.treasury_tokens.DIGG)


@pytest.fixture(scope="module", autouse=True)
def topup_and_fast_forward(dripper, badger):
    accounts[1].transfer(dripper, 1e18)
    badger._mint_for_testing(dripper, 100_000 * 10 ** badger.decimals())
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
    assert (
        dripper.start() + dripper.duration() > datetime.now().timestamp()
    ), "dripping period already expired; increase start or duration"


def test_release_from_owner(badger, dripper, owner):
    bal_before = badger.balanceOf(dripper.beneficiary())
    dripper.release(badger, {"from": owner})
    assert badger.balanceOf(dripper.beneficiary()) > bal_before


def test_accounting_released(dripper, badger):
    assert dripper.released(badger, {"from": accounts[1]}) > 0


def test_release_from_random(badger, dripper):
    # add some time to build up releasable funds again
    chain.sleep(dripper.interval())
    chain.mine()
    bal_before = badger.balanceOf(dripper.beneficiary())
    # release should not be permissionless anymore!
    with brownie.reverts("Only callable by owner"):
        dripper.release(badger, {"from": accounts[1]})
    assert badger.balanceOf(dripper.beneficiary()) == bal_before


def test_upkeep_needed(dripper, badger, keeper):
    assert chain.time() - dripper.start() > dripper.interval()
    assert badger.balanceOf(dripper) > 0
    upkeep_needed, assets_encoded = dripper.checkUpkeep(b"", {"from": keeper})
    assert upkeep_needed
    return upkeep_needed, assets_encoded


def test_perform_upkeep_while_paused(dripper, badger, keeper, owner):
    upkeep_needed, assets_encoded = test_upkeep_needed(dripper, badger, keeper)
    assert upkeep_needed
    dripper.pause({"from": owner})
    with brownie.reverts("Pausable: paused"):
        dripper.performUpkeep(assets_encoded, {"from": keeper})
    dripper.unpause({"from": owner})


def test_perform_upkeep_from_random(dripper, badger, keeper):
    upkeep_needed, assets_encoded = test_upkeep_needed(dripper, badger, keeper)
    bal_dripper_before = badger.balanceOf(dripper)
    bal_benef_before = badger.balanceOf(dripper.beneficiary())
    assert upkeep_needed
    with brownie.reverts("typed error: 0xd3a68034"):  # OnlyKeeperRegistry()
        dripper.performUpkeep(assets_encoded, {"from": accounts[1]})
    assert bal_dripper_before == badger.balanceOf(dripper)
    assert bal_benef_before == badger.balanceOf(dripper.beneficiary())


def test_perform_upkeep(dripper, badger, keeper):
    bal_dripper_before = badger.balanceOf(dripper)
    bal_benef_before = badger.balanceOf(dripper.beneficiary())
    upkeep_needed, assets_encoded = test_upkeep_needed(dripper, badger, keeper)
    assert upkeep_needed
    dripper.performUpkeep(assets_encoded, {"from": keeper})
    assert bal_dripper_before > badger.balanceOf(dripper)
    assert badger.balanceOf(dripper.beneficiary()) > bal_benef_before


def test_perform_upkeep_multiple_tokens(dripper, badger, digg, keeper):
    badger._mint_for_testing(dripper, 100_000 * 10 ** badger.decimals())
    digg._mint_for_testing(dripper, 10 * 10 ** digg.decimals())
    chain.sleep(dripper.interval())
    chain.mine()

    bal_dripper_before_badger = badger.balanceOf(dripper)
    bal_benef_before_badger = badger.balanceOf(dripper.beneficiary())
    bal_dripper_before_digg = digg.balanceOf(dripper)
    bal_benef_before_digg = digg.balanceOf(dripper.beneficiary())

    upkeep_needed, assets_encoded = test_upkeep_needed(dripper, badger, keeper)
    assert upkeep_needed
    dripper.performUpkeep(assets_encoded, {"from": keeper})
    assert bal_dripper_before_badger > badger.balanceOf(dripper)
    assert badger.balanceOf(dripper.beneficiary()) > bal_benef_before_badger
    assert bal_dripper_before_digg > digg.balanceOf(dripper)
    assert digg.balanceOf(dripper.beneficiary()) > bal_benef_before_digg


def test_sweep_eth_from_owner(dripper, owner):
    bal_before = owner.balance()
    dripper.sweep({"from": owner})
    assert owner.balance() > bal_before
    assert dripper.balance() == 0


def test_sweep_eth_from_random(dripper):
    with brownie.reverts():
        dripper.sweep({"from": accounts[1]})


def test_sweep_erc_from_owner(dripper, badger, owner):
    badger._mint_for_testing(dripper, 100_000 * 10 ** badger.decimals())
    bal_before = badger.balanceOf(owner)
    dripper.sweep(badger, {"from": owner})
    assert badger.balanceOf(owner) > bal_before
    assert badger.balanceOf(dripper) == 0


def test_sweep_erc_from_random(dripper, badger):
    with brownie.reverts():
        dripper.sweep(badger, {"from": accounts[1]})


def test_upkeep_not_needed(dripper, badger, keeper):
    assert chain.time() - dripper.start() > dripper.interval()
    assert badger.balanceOf(dripper) == 0
    upkeep_needed, _ = dripper.checkUpkeep(b"", {"from": keeper})
    assert not upkeep_needed
