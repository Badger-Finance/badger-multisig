from calendar import timegm
from datetime import date, timedelta

from brownie import AutonomousDripper, accounts, chain

from helpers.addresses import registry


def main(deployer_label=None):
    deployer = accounts[0] if not deployer_label else accounts.load(deployer_label)
    if chain.id == 1:
        return AutonomousDripper.deploy(
            registry.eth.badger_wallets.badgertree,
            timegm(date(2022, 4, 20).timetuple()),
            int(timedelta(weeks=9).total_seconds()),
            60*60*24*7,
            [
                '0x3472A5A71965499acd81997a54BBA8D852C6E53d', # BADGER
                '0x798D1bE841a82a273720CE31c822C61a67a601C3' # DIGG
            ],
            registry.eth.chainlink.keeper_registry,
            {'from': deployer},
            # TODO: programmatically set to True when on a non-forked, live network
            publish_source=False#True
        )
    elif chain.id == 4:
        return AutonomousDripper.deploy(
            registry.rinkeby.badger_wallets.solo_multisig,
            timegm(date.today().timetuple()),
            int(timedelta(weeks=1).total_seconds()),
            60*60, # interval of one hour
            [
                '0xc7AD46e0b8a400Bb3C915120d284AafbA8fc4735', # rinkeby DAI
                '0x577D296678535e4903D59A4C929B718e1D575e0A' # rinkeby WBTC
            ],
            registry.rinkeby.chainlink.keeper_registry,
            {'from': deployer},
            # TODO: programmatically set to True when on a non-forked, live network
            publish_source=True
        )
