import calendar
from datetime import date, timedelta

from brownie import RemBadgerDripper, accounts

from helpers.addresses import registry


def main(deployer=accounts[0]):
    dripper = RemBadgerDripper.deploy(
        registry.eth.sett_vaults.remBADGER,
        calendar.timegm(date(2022, 4, 15).timetuple()),
        int(timedelta(weeks=11).total_seconds()),
        {'from': deployer},
        publish_source=False#True
    )

    print(dripper.beneficiary())
    print(dripper.start())
    print(dripper.duration())
