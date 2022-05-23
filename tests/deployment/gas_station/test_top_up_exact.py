import brownie


def test_from_0_to_min_balance(gas_station, random, keeper):
    assert gas_station.balance() > 0
    assert random.balance() == 0

    gas_station.setWatchList(
        [random.address], [1e18], [.1e18], {'from': gas_station.owner()}
    )

    upkeep_needed, data = gas_station.checkUpkeep(b'', {'from': keeper})
    assert upkeep_needed

    gas_station.performUpkeep(data, {'from': keeper})
    assert random.balance() == 1e18


def test_from_0_to_min_balance_from_random(gas_station, random, keeper):
    assert gas_station.balance() > 0
    assert random.balance() == 0

    gas_station.setWatchList(
        [random.address], [1e18], [.1e18], {'from': gas_station.owner()}
    )

    upkeep_needed, data = gas_station.checkUpkeep(b'', {'from': keeper})
    assert upkeep_needed

    with brownie.reverts('typed error: 0xd3a68034'): # onlyKeeperRegistry
        gas_station.performUpkeep(data, {'from': random})
    assert random.balance() == 0


def test_empty_gas_station(gas_station, random, keeper):
    # empty the station first
    gas_station.withdraw(
        gas_station.balance(),
        gas_station.owner(),
        {'from': gas_station.owner()}
    )
    assert gas_station.balance() == 0
    assert random.balance() == 0

    gas_station.setWatchList(
        [random.address], [1e18], [.1e18], {'from': gas_station.owner()}
    )

    upkeep_needed, _ = gas_station.checkUpkeep(b'', {'from': keeper})
    assert not upkeep_needed


def test_min_balance_already_met(gas_station, random, deployer, keeper):
    assert gas_station.balance() > 0
    assert random.balance() == 0

    gas_station.setWatchList(
        [random.address], [1e18], [.1e18], {'from': gas_station.owner()}
    )

    # seed random from deployer with > 1e18
    deployer.transfer(random, 2e18)

    upkeep_needed, data = gas_station.checkUpkeep(b'', {'from': keeper})
    assert not upkeep_needed

    return upkeep_needed, data


def test_malicious_keeper(gas_station, random, deployer, keeper):
    upkeep_needed, data = test_min_balance_already_met(
        gas_station, random, deployer, keeper
    )

    assert not upkeep_needed

    # perform the upkeep anyway; should not alter balances
    bal_before_gas_station = gas_station.balance()
    bal_before_random = random.balance()
    gas_station.performUpkeep(data, {'from': keeper})
    assert gas_station.balance() == bal_before_gas_station
    assert random.balance() == bal_before_random
