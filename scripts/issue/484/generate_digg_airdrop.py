from decimal import Decimal, getcontext

import pandas as pd

from helpers.addresses import registry


# maximum precision needed for $digg
getcontext().prec = 9


def main():
    # csv export of technical post mortem sheet:
    # https://docs.google.com/spreadsheets/d/1IPwk-_ZtZ3aIxaJgYm8wZ7W6biB65Ou46lkYnniAHzQ/edit#gid=168062083
    df = pd.read_csv(
        "scripts/issue/5/assets_stolen_recoverable-_transferFrom.csv",
        converters={"value_digg": Decimal},
    )

    # enforce precision of 9 on input
    df["value_digg"] = df["value_digg"] / 1

    # filter out victims for which:
    # - funds have already been recovered, and
    # - no underlying $digg exists
    recovered = df[df["type"] == "recoverable"]["victim"]
    dff = df[~df["victim"].isin(recovered) & df["value_digg"] > 0].copy()

    # # add the $remdigg token address and other gnosis airdrop app columns
    dff["token_type"] = "erc20"
    dff["token_addr"] = registry.eth.treasury_tokens.DIGG
    dff["id"] = pd.NA

    # # build dataframe for airdrop;
    # # filter on value > 0 and take only the necessary columns
    airdrop = dff[["token_type", "token_addr", "victim", "value_digg", "id"]]

    # # dump df to csv for gnosis csv airdrop app
    airdrop.to_csv(
        "scripts/issue/484/airdrop_bip92.csv",
        index=False,
        header=["token_type", "token_address", "receiver", "value", "id"],
    )
    print(airdrop)
    print(airdrop["value_digg"].sum())
