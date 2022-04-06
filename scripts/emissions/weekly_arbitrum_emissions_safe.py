import os
import json
import datetime
from rich.console import Console
from brownie import Wei
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

C = Console()

# 7 days
DURATION = 604800


def main(target_file="generated_emissions_info_BIP_88"):
    path = os.getcwd() + f"/scripts/emissions/{target_file}.json"
    with open(path) as f:
        data = json.load(f)

    weekly_emissions(data)


def weekly_emissions(data):
    today = datetime.date.today()
    target_week = find_thrusday(today)

    emissions_data = data[target_week.strftime("%d-%m-%y")]
    time_range = emissions_data["timerange"]

    safe = GreatApeSafe(registry.arbitrum.badger_wallets.techops_multisig)

    rewards_logger = safe.contract(registry.arbitrum.rewardsLogger)

    totals = {"badger": 0}

    for sett in emissions_data["setts"]:
        # filter only for ARBITRUM network
        if sett["network"] == "ARBITRUM":
            beneficiary = sett["address"]

            if sett["badger_allocation"] != 0:
                formatted_amount = Wei(f'{sett["badger_allocation"]} ether')

                totals["badger"] += formatted_amount

                rewards_logger.setUnlockSchedule(
                    beneficiary,
                    registry.arbitrum.treasury_tokens.BADGER,
                    formatted_amount,
                    time_range["starttime"],
                    time_range["endtime"],
                    DURATION,
                )

    # console output
    C.print(
        f"Total emissions during {target_week.strftime('%d-%m-%y')} : badger={totals['badger']/10**18}"
    )

    safe.post_safe_tx()


def find_thrusday(date):
    THRUSDAY = 4
    year, week, day = date.isocalendar()
    delta = datetime.timedelta(days=THRUSDAY - day)
    return date + delta
