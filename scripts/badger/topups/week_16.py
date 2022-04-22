import pandas as pd
from decimal import Decimal

from helpers.addresses import registry


def main():
    """
    build a gnosis airdrop csv with all topups needing to happen for a given
    week.
    """

    df = {"token_address": [], "receiver": [], "value": []}

    # https://github.com/Badger-Finance/badger-multisig/issues/383
    # add badger to the tree for weekly emissions
    week_15_badger_emissions = Decimal('20_000')
    week_15_rembadger_emissions = Decimal('7692.307692')
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.badger_wallets.badgertree)
    df["value"].append(
        week_15_badger_emissions + week_15_rembadger_emissions
    )

    # https://github.com/Badger-Finance/badger-multisig/issues/384
    # add digg to the tree for weekly emissions
    week_15_digg_emissions_tree = Decimal('1.302461219')
    df["token_address"].append(registry.eth.treasury_tokens.DIGG)
    df["receiver"].append(registry.eth.badger_wallets.badgertree)
    df["value"].append(week_15_digg_emissions_tree)

    # turn dict of lists into dataframe and add additional columns needed by
    # the gnosis app
    df = pd.DataFrame(df)
    df["token_type"] = "erc20"
    df["id"] = pd.NA

    # build dataframe for airdrop and dump to csv
    airdrop = df[["token_type", "token_address", "receiver", "value", "id"]]
    airdrop.to_csv(
        "scripts/badger/topups/week_16.csv",
        index=False,
        header=["token_type", "token_address", "receiver", "value", "id"],
    )
    print(airdrop)
