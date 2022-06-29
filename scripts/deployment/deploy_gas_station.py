from brownie import GasStationExact, accounts, chain, network

from helpers.addresses import registry


def main(deployer_label=None):
    deployer = accounts[0] if not deployer_label else accounts.load(deployer_label)
    on_live_network = not '-fork' in network.show_active()
    if chain.id == 1:
        return GasStationExact.deploy(
            registry.eth.chainlink.keeper_registry,
            60 * 60 * 24,
            {'from': deployer},
            publish_source=on_live_network
        )
    elif chain.id == 4:
        return GasStationExact.deploy(
            registry.rinkeby.chainlink.keeper_registry,
            60 * 60,
            {'from': deployer},
            publish_source=on_live_network
        )
