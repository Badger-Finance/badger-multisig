import os
import json
import datetime
from rich.console import Console
from brownie import Wei
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from decimal import Decimal

C = Console()

# 7 days
WEEK_DURATION = 604800


def main(target_file="generated_emissions_info_BIP_88_Emissions"):
    path = os.getcwd() + f"/scripts/emissions/{target_file}.json"
    with open(path) as f:
        data = json.load(f)

    weekly_emissions(data)


def weekly_emissions(data):
    today = datetime.date.today()
    target_week = find_thrusday(today)

    emissions_data = data[target_week.strftime("%d-%m-%y")]
    time_range = emissions_data["timerange"]

    last_quarter_time_rage = list(data.keys())[-1]
    end_quarter_timestamp = data[last_quarter_time_rage]["timerange"]["endtime"]

    safe = GreatApeSafe(registry.arbitrum.badger_wallets.techops_multisig)

    rewards_logger = safe.contract(registry.arbitrum.rewardsLogger)

    totals = {"badger": 0}

    duration = end_quarter_timestamp - time_range["starttime"]

    weeks_no = duration / WEEK_DURATION

    for sett in emissions_data["setts"]:
        # filter only for ARBITRUM network
        if sett["network"] == "ARBITRUM":
            beneficiary = sett["address"]

            if sett["badger_allocation"] != 0:
                formatted_amount = Wei(
                    f'{Decimal(sett["badger_allocation"] * weeks_no)} ether'
                )

                totals["badger"] += formatted_amount

                rewards_logger.setUnlockSchedule(
                    beneficiary,
                    registry.arbitrum.treasury_tokens.BADGER,
                    formatted_amount,
                    time_range["starttime"],
                    end_quarter_timestamp,
                    duration,
                )

    # console output
    C.print(
        f"Total emissions during {target_week.strftime('%d-%m-%y')} to {datetime.datetime.fromtimestamp(end_quarter_timestamp).strftime('%d-%m-%y')}: badger={totals['badger']/10**18}"
    )

    safe.post_safe_tx()


def find_thrusday(date):
    THRUSDAY = 4
    year, week, day = date.isocalendar()
    delta = datetime.timedelta(days=THRUSDAY - day)
    return date + delta
