"""the EthBalanceMonitor contract, which was used as a base for
GasStationExact, already has been tested extensively by chainlink. the
following unit tests only cover the changes made to that base contract.

existing tests: https://github.com/smartcontractkit/chainlink/blob/develop/contracts/test/v0.8/EthBalanceMonitor.test.ts
diff with EthBalanceMonitor.sol: https://www.diffchecker.com/mMyjvPXl"""


import pytest

from brownie import Contract, accounts, interface
from brownie_tokens import MintableForkToken

from helpers.addresses import registry


@pytest.fixture(scope="module")
def deployer():
    return accounts[0]


@pytest.fixture(scope="module")
def gas_station():
    from scripts.deployment.deploy_gas_station import main

    return main()


@pytest.fixture(scope="module")
def keeper(gas_station):
    return interface.IKeeperRegistry(gas_station.getKeeperRegistryAddress())


@pytest.fixture
def random():
    return accounts.add()


@pytest.fixture(autouse=True)
def seed_the_station(gas_station):
    accounts[0].transfer(gas_station, 5e18)


@pytest.fixture
def dai():
    addr = registry.eth.treasury_tokens.DAI
    Contract.from_explorer(addr)
    return MintableForkToken(addr)
