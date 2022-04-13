import os
from decimal import Decimal
import json
import datetime
from rich.console import Console
from brownie import Wei, Contract
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from scripts.emissions.dynamic_tvl_emissions import (
    dynamic_bveCVX_emissions,
)

console = Console()

# addresses involved
treasury_tokens = registry.eth.treasury_tokens
sett_vaults = registry.eth.sett_vaults


# remove autocompound_50_setts as per issue: https://github.com/Badger-Finance/badger-ape/issues/572

AUTOCOMPOUND_100_SETTS = [
    sett_vaults["bDIGG"],
]

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

    # do dynamically and sometimes we may have shifts or trials for sync some sett
    DURATION = end_quarter_timestamp - time_range["starttime"]

    weeks_no = DURATION / WEEK_DURATION

    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    digg = safe.contract(treasury_tokens["DIGG"])

    #bcvxCRV = safe.contract(sett_vaults["bcvxCRV"])

    rewards_logger = safe.contract(registry.eth.rewardsLogger)

    totals = {"badger": 0, "digg": 0, "bcvxCRV": 0}

    for sett in emissions_data["setts"]:
        # filter only for ETHEREUM network
        if sett["network"] == "ETHEREUM":
            beneficiary = sett["address"]

            if sett["badger_allocation"] != 0:
                #  make difference between native setts as per WeeklyEmissions.md
                if beneficiary in AUTOCOMPOUND_100_SETTS:
                    continue  # nothing to emit
                else:
                    formatted_amount = Wei(f'{Decimal(sett["badger_allocation"] * weeks_no)} ether')

                totals["badger"] += formatted_amount

                rewards_logger.setUnlockSchedule(
                    beneficiary,
                    treasury_tokens["BADGER"],
                    formatted_amount,
                    time_range["starttime"],
                    end_quarter_timestamp,
                    DURATION,
                )
            if sett["digg_allocation"] != 0:
                if beneficiary in AUTOCOMPOUND_100_SETTS:
                    continue
                else:
                    initial_fragments = sett["digg_allocation"] * 10 ** digg.decimals()
                    shares = Decimal(
                        (initial_fragments * digg._initialSharesPerFragment()) * weeks_no
                    )

                totals["digg"] += shares

                rewards_logger.setUnlockSchedule(
                    beneficiary,
                    treasury_tokens["DIGG"],
                    shares,
                    time_range["starttime"],
                    end_quarter_timestamp,
                    DURATION,
                )

    # handle individually out of loop scope emissions for `bveCVX` as changes from BIP-75, they may change also in future better to leave them more accessible

    """
    #### LEAVING IT FOR RECORDS, REMOVED AS PER BIP-87 ####
    
    LINK -> https://forum.badger.finance/t/bip-87-bvecvx-restructure-voting-strategy-and-emissions-revised-with-community-feedback/5521

    # 1. here we will handle the cvxCrv emissions - pffs checkup for bcvxCRV sett
    # 20k as per BIP-75
    weekly_cvxCrv_target_amount = 20000
    bcvxCRV_ppfs = bcvxCRV.getPricePerFullShare() / 10 ** bcvxCRV.decimals()
    bcvxCrv_to_emit = weekly_cvxCrv_target_amount / bcvxCRV_ppfs

    totals["bcvxCRV"] += bcvxCrv_to_emit

    rewards_logger.setUnlockSchedule(
        sett_vaults["bveCVX"],
        sett_vaults["bcvxCRV"],
        Wei(f"{bcvxCrv_to_emit} ether"),
        time_range["starttime"],
        time_range["endtime"],
        DURATION,
    )

    # 2. Badger emissions for `bveCVX` 15%apr - BIP-75
    formatted_badger_amount_bveCVX = dynamic_bveCVX_emissions()
    totals["badger"] += formatted_badger_amount_bveCVX

    rewards_logger.setUnlockSchedule(
        sett_vaults["bveCVX"],
        treasury_tokens["BADGER"],
        formatted_badger_amount_bveCVX,
        time_range["starttime"],
        time_range["endtime"],
        DURATION,
    )
    """

    # console output
    print(
        f"Total emissions during {target_week.strftime('%d-%m-%y')} to {datetime.datetime.fromtimestamp(end_quarter_timestamp).strftime('%d-%m-%y')}: badger={totals['badger']/10**18}, digg={totals['digg']} and bcvxCrv={totals['bcvxCRV']}"
    )

    safe.post_safe_tx()


def find_thrusday(date):
    THRUSDAY = 4
    year, week, day = date.isocalendar()
    delta = datetime.timedelta(days=THRUSDAY - day)
    return date + delta
