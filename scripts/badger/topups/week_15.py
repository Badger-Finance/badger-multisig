import pandas as pd
from decimal import Decimal

from helpers.addresses import registry


def main():
    """
    build a gnosis airdrop csv with all topups needing to happen for a given
    week.
    """

    df = {"token_address": [], "receiver": [], "value": []}

    # https://github.com/Badger-Finance/badger-multisig/issues/345
    # add badger to the tree for weekly emissions
    week_15_badger_emissions = Decimal("20_000")
    week_15_rembadger_emissions = Decimal("7692.307692")
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.badger_wallets.badgertree)
    df["value"].append(week_15_badger_emissions + week_15_rembadger_emissions)

    # https://github.com/Badger-Finance/badger-multisig/issues/344
    # add digg to the tree for weekly emissions
    week_15_digg_emissions_tree = Decimal("1.302461219")
    df["token_address"].append(registry.eth.treasury_tokens.DIGG)
    df["receiver"].append(registry.eth.badger_wallets.badgertree)
    df["value"].append(week_15_digg_emissions_tree)

    # add digg to rewards for weekly emissions
    week_15_digg_emissions_rewards = Decimal("0.325615304")
    df["token_address"].append(registry.eth.treasury_tokens.DIGG)
    df["receiver"].append(registry.eth.badger_wallets.native_autocompounder)
    df["value"].append(week_15_digg_emissions_rewards)

    # https://github.com/Badger-Finance/badger-multisig/issues/343
    # biweekly rembadger deposit
    week_15_rembadger_deposit = Decimal("11538.461538")
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.sett_vaults.remBADGER)
    df["value"].append(week_15_rembadger_deposit)

    # turn dict of lists into dataframe and add additional columns needed by
    # the gnosis app
    df = pd.DataFrame(df)
    df["token_type"] = "erc20"
    df["id"] = pd.NA

    # build dataframe for airdrop and dump to csv
    airdrop = df[["token_type", "token_address", "receiver", "value", "id"]]
    airdrop.to_csv(
        "scripts/badger/topups/week_15.csv",
        index=False,
        header=["token_type", "token_address", "receiver", "value", "id"],
    )
    print(airdrop)
