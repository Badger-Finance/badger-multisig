from  calendar import timegm
from datetime import date, timedelta

from brownie import EmissionsDripper, accounts

from helpers.addresses import registry


def main(deployer_label=None):
    deployer = accounts[0] if not deployer_label else accounts.load(deployer_label)
    return EmissionsDripper.deploy(
        registry.eth.sett_vaults.remBADGER,
        timegm(date(2022, 4, 29).timetuple()),
        int(timedelta(weeks=9).total_seconds()),
        registry.eth.badger_wallets.techops_multisig,
        registry.eth.badger_wallets.dev_multisig,
        deployer,
        {'from': deployer},
        publish_source=False#True
    )


def rinkeby(deployer_label=None):
    deployer = accounts.load(deployer_label)
    return EmissionsDripper.deploy(
        registry.rinkeby.badger_wallets.solo_multisig,
        timegm(date(2022, 4, 15).timetuple()),
        int(timedelta(weeks=11).total_seconds()),
        registry.rinkeby.badger_wallets.rinkeby_multisig,
        registry.rinkeby.badger_wallets.rinkeby_multisig,
        deployer,
        {'from': deployer},
        publish_source=True
    )