import pandas as pd
import os

from helpers.addresses import registry


path_dirname = f"{os.path.dirname(__file__)}/distributions_csv"

eps_address = registry.bsc.airdropable_tokens.EPS


def main():
    # create directory
    os.makedirs(f"{os.path.dirname(__file__)}/distribution_csv_gnosis", exist_ok=True)
    # convert all to gnosis format
    for file in os.listdir(path_dirname):
        # address, amount
        df = pd.read_csv(f"{path_dirname}/{file}")

        # into new csv gnosis format
        df["token_type"] = "erc20"
        df["token_address"] = eps_address
        df["id"] = ""

        # reorder
        df_reorder = df[["token_type", "token_address", "address", "amount", "id"]]

        df_reorder.to_csv(
            f"{os.path.dirname(__file__)}/distribution_csv_gnosis/{file}",
            index=False,
            header=["token_type", "token_address", "receiver", "value", "id"],
        )
