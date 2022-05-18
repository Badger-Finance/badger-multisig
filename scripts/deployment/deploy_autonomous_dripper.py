from calendar import timegm
from datetime import date, timedelta

from brownie import AutonomousDripper, accounts, chain, network

from helpers.addresses import registry


def main(deployer_label=None):
    deployer = accounts[0] if not deployer_label else accounts.load(deployer_label)
    if chain.id == 1:
        return AutonomousDripper.deploy(
            registry.eth.badger_wallets.techops_multisig, # address initialOwner
            registry.eth.badger_wallets.badgertree, # address beneficiaryAddress
            timegm(date(2022, 5, 20).timetuple()), # uint64 startTimestamp
            int(timedelta(weeks=6).total_seconds()), # uint64 durationSeconds
            60*60*24*7, # uint intervalSeconds
            [
                registry.eth.treasury_tokens.BADGER,
                registry.eth.treasury_tokens.DIGG,
            ], # address[] memory watchlistAddresses
            registry.eth.chainlink.keeper_registry, # address keeperRegistryAddress
            {'from': deployer},
            publish_source=(not '-fork' in network.show_active())
        )
    elif chain.id == 4:
        return AutonomousDripper.deploy(
            deployer,
            registry.rinkeby.badger_wallets.solo_multisig,
            timegm(date.today().timetuple()),
            int(timedelta(weeks=1).total_seconds()),
            60*60, # interval of one hour
            [
                registry.eth.treasury_tokens.DAI,
                registry.eth.treasury_tokens.WBTC,
            ],
            registry.rinkeby.chainlink.keeper_registry,
            {'from': deployer},
            # TODO: programmatically set to True when on a non-forked, live network
            publish_source=(not '-fork' in network.show_active())
        )
