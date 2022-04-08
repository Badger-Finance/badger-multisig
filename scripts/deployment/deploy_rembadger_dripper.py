from  calendar import timegm
from datetime import date, timedelta

from brownie import RemBadgerDripper, accounts

from helpers.addresses import registry


def main(deployer=accounts[0]):
    return RemBadgerDripper.deploy(
        registry.eth.sett_vaults.remBADGER,
        timegm(date(2022, 4, 29).timetuple()),
        int(timedelta(weeks=9).total_seconds()),
        deployer,
        {'from': deployer},
        publish_source=False#True
    )
