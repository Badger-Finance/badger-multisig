import sys
import csv
import datetime
import json
import os
from typing import Dict, List
from rich.console import Console

console = Console()

# 7 days
DURATION = 604800

# 17 hours to offset new emissions
OFFSET_HOURS = 61200


def main(file_name):
    path = os.getcwd() + f"/scripts/emissions/{file_name}.csv"

    emissions_json = {}

    with open(path) as emissions_csv:
        emissions_reader = csv.reader(emissions_csv, delimiter=",")
        for row_index, row in enumerate(emissions_reader):
            # Check the header of the CSV to populate date_timestamps
            if row_index == 0:
                date_indexes = get_date_indexes(row)
                if len(date_indexes) == 0:
                    raise Exception("Formatting Error: No dates in provided JSON")
                for index in date_indexes:
                    date = row[index]
                    hour = 17 if date == "18-11-21" else 0
                    date_timestamp = get_start_time(date, hour)
                    offset = OFFSET_HOURS if date == "18-11-21" else 0
                    json_data = {
                        "timerange": {
                            "starttime": date_timestamp,
                            "endtime": date_timestamp + DURATION - offset,
                        },
                        "setts": [],
                    }
                    emissions_json[date] = json_data
            else:
                name = row[0]
                address = row[1]
                network = row[2]
                # iterate through the date indexes to populate the emissions schedules for each date
                for index, date in date_indexes.items():
                    try:
                        token_amount = float(row[index].replace(",", ""))
                        if token_amount == 0:
                            continue

                        emissions_json[date]["setts"].append(
                            {
                                "network": network,
                                "name": name,
                                "address": address,
                                "badger_allocation": token_amount
                                if row[3] == "BADGER"
                                else 0,
                                "digg_allocation": token_amount
                                if row[3] == "DIGG"
                                else 0,
                            }
                        )
                    except:
                        continue

        eth_path = (
            os.getcwd()
            + f"/scripts/emissions/generated_emissions_info_{file_name}.json"
        )
        with open(eth_path, "w") as eth_outfile:
            json.dump(emissions_json, eth_outfile, indent=4)


def get_date_indexes(row: List[str]) -> Dict[int, str]:
    """
    Reads the header of the CSV to find the indexes of date rows
    param: row = List containing header row of the CSV
    returns: Dict containing the index: date combination for reference
    """
    date_indexs = {}
    for index, date in enumerate(row):
        try:
            datetime.datetime.strptime(date, "%d-%m-%y")
            date_indexs[index] = date
        except:
            print(f"index {index} did not contain a valid formatted date: {date}")
            pass
    return date_indexs


def get_start_time(date: str, hour: int = 0) -> int:
    """
    Takes a date string and returns the unix timestamp for 1700 UTC (Badger Emissions Start Time)
    param: date = String formatted date in DD-MM-YY format
    returns: unix timestamp for 0 UTC (Badger emissions start time)
    """
    date = datetime.datetime.strptime(date, "%d-%m-%y")
    date = date.replace(hour=hour, tzinfo=datetime.timezone.utc)
    return int(date.timestamp())


if __name__ == "__main__":
    # accept an arg in cli to point to which csv we want to generate the json file from
    main(sys.argv[1])
