import pandas as pd
import os

path_dirname = f"{os.path.dirname(__file__)}/distribution_csv_gnosis"

# PUT HERE THE FILES TO GENERATE FROM THE BIG CSV PAYLOAD FILE
PAYLOAD_FILES = [
    "distribution-2022-01-06.csv",
    "distribution-2022-01-13.csv",
    "distribution-2022-01-20.csv",
    "distribution-2022-01-27.csv",
]


def main():
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

    payload_df = payload_df.sort_values(by=["value"], ascending=False)

    # leave id section blank
    payload_df['id'] = ''

    payload_df.to_csv(
        f"{os.path.dirname(__file__)}/payload_gnosis_csv/{PAYLOAD_FILES[0].replace('.csv', '')}_until_{PAYLOAD_FILES[-1].replace('.csv', '')}.csv",
        index=False,
        header=["token_type", "token_address", "receiver", "value", "id"],
    )