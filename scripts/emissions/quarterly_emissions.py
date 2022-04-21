import os
from decimal import Decimal
import json
from datetime import date, datetime, timedelta
from rich.console import Console

from brownie import Wei, network

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

C = Console()

# 7 days
WEEK_DURATION = 604800


def main(target_file="generated_emissions_info_BIP_88_Emissions"):
    path = os.getcwd() + f"/scripts/emissions/{target_file}.json"
    with open(path) as f:
        data = json.load(f)

    # common times for Arb & Eth chain
    today = date.today()
    target_week = find_thrusday(today)

    emissions_data = data[target_week.strftime("%d-%m-%y")]
    time_range = emissions_data["timerange"]

    last_quarter_time_rage = list(data.keys())[-1]
    end_quarter_timestamp = data[last_quarter_time_rage]["timerange"]["endtime"]

    duration = end_quarter_timestamp - time_range["starttime"]

    weeks_no = duration / WEEK_DURATION

    # not emitting bcvxCRV since new emissions of Q2-2022!
    totals = {"badger": 0, "digg": 0}

    # logic based on-chain
    if network.chain.id == 1:
        # remove autocompound_50_setts as per issue: https://github.com/Badger-Finance/badger-ape/issues/572
        AUTOCOMPOUND_100_SETTS = [
            registry.eth.sett_vaults.bDIGG,
        ]

        safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
        rewards_logger = safe.contract(registry.eth.rewardsLogger)

        digg = safe.contract(registry.eth.treasury_tokens.DIGG)

        for sett in emissions_data["setts"]:
            if sett["network"] == "ETHEREUM":
                beneficiary = sett["address"]

                if sett["badger_allocation"] != 0:
                    #  make difference between native setts as per WeeklyEmissions.md
                    if beneficiary in AUTOCOMPOUND_100_SETTS:
                        continue  # nothing to emit
                    else:
                        formatted_amount = Wei(
                            f'{Decimal(sett["badger_allocation"] * weeks_no)} ether'
                        )

                    totals["badger"] += formatted_amount

                    rewards_logger.setUnlockSchedule(
                        beneficiary,
                        registry.eth.treasury_tokens.BADGER,
                        formatted_amount,
                        time_range["starttime"],
                        end_quarter_timestamp,
                        duration,
                    )

                if sett["digg_allocation"] != 0:
                    if beneficiary in AUTOCOMPOUND_100_SETTS:
                        continue
                    else:
                        initial_fragments = (
                            sett["digg_allocation"] * 10 ** digg.decimals()
                        )
                        shares = Decimal(
                            (initial_fragments * digg._initialSharesPerFragment())
                            * weeks_no
                        )

                totals["digg"] += shares

                rewards_logger.setUnlockSchedule(
                    beneficiary,
                    registry.eth.treasury_tokens.DIGG,
                    shares,
                    time_range["starttime"],
                    end_quarter_timestamp,
                    duration,
                )
    elif network.chain.id == 42161:
        safe = GreatApeSafe(registry.arbitrum.badger_wallets.techops_multisig)
        rewards_logger = safe.contract(registry.arbitrum.rewardsLogger)

        for sett in emissions_data["setts"]:
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
        f"Total emissions during {target_week.strftime('%d-%m-%y')} to {datetime.fromtimestamp(end_quarter_timestamp).strftime('%d-%m-%y')}: badger={totals['badger']/1e18} & digg={totals['digg']}"
    )

    safe.post_safe_tx()


def find_thrusday(date):
    THRUSDAY = 4
    _, _, day = date.isocalendar()
    delta = timedelta(days=THRUSDAY - day)
    return date + delta
