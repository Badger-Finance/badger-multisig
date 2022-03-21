from pycoingecko import CoinGeckoAPI

import pandas as pd
import os

path_dirname = f"{os.path.dirname(__file__)}/distribution_csv_gnosis"

# PUT HERE THE FILES TO GENERATE FROM THE BIG CSV PAYLOAD FILE
PAYLOAD_FILES = [
    "distribution-2022-02-03.csv",
    "distribution-2022-02-10.csv",
    "distribution-2022-02-17.csv",
    "distribution-2022-02-24.csv",
]


def main():
    cg = CoinGeckoAPI()

    spot_eps_price = cg.get_price(ids="ellipsis", vs_currencies="usd")["ellipsis"][
        "usd"
    ]

    distribution_threshold = 1 / spot_eps_price

    # for records to drop it into ticket
    print(f"\nThreshold is {distribution_threshold} EPSs and current EPS price is ${spot_eps_price}\n")

    # create directory
    os.makedirs(f"{os.path.dirname(__file__)}/payload_gnosis_csv", exist_ok=True)

    column_names = ["token_type", "token_address", "receiver", "value", "id"]
    payload_df = pd.DataFrame(columns=column_names)

    for file in os.listdir(path_dirname):
        # filter out those are not in payload
        if file in PAYLOAD_FILES:
            df = pd.read_csv(f"{path_dirname}/{file}")

            payload_df = (
                pd.concat([df, payload_df])
                .groupby(["token_type", "token_address", "receiver"])
                .sum()
                .reset_index()
            )

    # removes dusty, only distribute those >= $1 of value
    payload_df = payload_df[payload_df["value"] >= distribution_threshold]

    payload_df = payload_df.sort_values(by=["value"], ascending=False)

    # leave id section blank
    payload_df["id"] = ""

    payload_df.to_csv(
        f"{os.path.dirname(__file__)}/payload_gnosis_csv/{PAYLOAD_FILES[0].replace('.csv', '')}_until_{PAYLOAD_FILES[-1].replace('.csv', '')}.csv",
        index=False,
        header=["token_type", "token_address", "receiver", "value", "id"],
    )
