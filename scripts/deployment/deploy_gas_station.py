from brownie import GasStationExact, accounts, chain

from helpers.addresses import registry


def main(deployer_label=None):
    deployer = accounts[0] if not deployer_label else accounts.load(deployer_label)
    if chain.id == 1:
        return GasStationExact.deploy(
            registry.eth.chainlink.keeper_registry,
            60*60,
            {'from': deployer},
            # TODO: programmatically set to True when on a non-forked, live
            # network opposed to running tests on main
            publish_source=False#True
        )
    elif chain.id == 4:
        return GasStationExact.deploy(
            registry.rinkeby.chainlink.keeper_registry,
            60*60,
            {'from': deployer},
            # TODO: programmatically set to True when on a non-forked, live
            # network opposed to running tests on main
            publish_source=True
        )
