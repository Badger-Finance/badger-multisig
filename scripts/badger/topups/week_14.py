import pandas as pd
from decimal import Decimal

from helpers.addresses import registry


def main():
    """
    build a gnosis airdrop csv with all topups needing to happen for a given
    week.
    """

    df = {"token_address": [], "receiver": [], "value": []}

    # https://github.com/Badger-Finance/badger-multisig/issues/323
    # add badger to the tree for weekly emissions
    week_14_badger_emissions = Decimal('20_000')
    week_14_rembadger_emissions = Decimal('7692.307692')
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.badger_wallets.badgertree)
    # multiply by two to catch up on week 13
    df["value"].append(
        (week_14_badger_emissions + week_14_rembadger_emissions) * 2
    )

    # https://github.com/Badger-Finance/badger-multisig/issues/324
    # add digg to the tree for weekly emissions
    week_13_14_digg_emissions = Decimal('3')
    df["token_address"].append(registry.eth.treasury_tokens.DIGG)
    df["receiver"].append(registry.eth.badger_wallets.badgertree)
    df["value"].append(week_13_14_digg_emissions)

    # https://github.com/Badger-Finance/badger-multisig/issues/320
    # catch up on rembadger
    week_13_rembadger_deposit = Decimal('11538.461538')
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.sett_vaults.remBADGER)
    df["value"].append(week_13_rembadger_deposit)

    # https://github.com/Badger-Finance/badger-multisig/issues/328
    # bridge badger to arbitrum through eoa
    q2_arb1_emissions = Decimal('11141')
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.badger_wallets.ops_executor3)
    df["value"].append(q2_arb1_emissions)

    # turn dict of lists into dataframe and add additional columns needed by
    # the gnosis app
    df = pd.DataFrame(df)
    df["token_type"] = "erc20"
    df["id"] = pd.NA

    # build dataframe for airdrop and dump to csv
    airdrop = df[["token_type", "token_address", "receiver", "value", "id"]]
    airdrop.to_csv(
        "scripts/badger/topups/week_14.csv",
        index=False,
        header=["token_type", "token_address", "receiver", "value", "id"],
    )
    print(airdrop)
