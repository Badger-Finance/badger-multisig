import pandas as pd
from brownie import interface
from decimal import Decimal

from helpers.addresses import registry


def main():
    """
    build a gnosis airdrop csv with all topups needing to happen for a given
    week.
    """

    df = {"token_address": [], "receiver": [], "value": []}

    # https://github.com/Badger-Finance/badger-multisig/issues/293
    # add badger to the tree for weekly emissions
    week_12_badger_emissions = Decimal("23994.02")
    week_12_rembadger_emissions = Decimal("7692.307692")
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.badger_wallets.badgertree)
    df["value"].append(week_12_badger_emissions + week_12_rembadger_emissions)

    # https://github.com/Badger-Finance/badger-multisig/issues/294
    # add badger to the tree for weekly emissions
    week_12_digg_emissions = Decimal("1.302461219")
    df["token_address"].append(registry.eth.treasury_tokens.DIGG)
    df["receiver"].append(registry.eth.badger_wallets.badgertree)
    df["value"].append(week_12_digg_emissions)

    # https://github.com/Badger-Finance/badger-multisig/issues/302
    # move bvecvx and related positions to treasury voter
    bvecvx_bal = interface.ISettV4h(
        registry.eth.treasury_tokens.bveCVX,
        owner=registry.eth.badger_wallets.treasury_ops_multisig,
    ).balanceOf(registry.eth.badger_wallets.treasury_ops_multisig)
    df["token_address"].append(registry.eth.treasury_tokens.bveCVX)
    df["receiver"].append(registry.eth.badger_wallets.treasury_voter_multisig)
    df["value"].append(Decimal(bvecvx_bal) / Decimal("1e18"))

    # turn dict of lists into dataframe and add additional columns needed by
    # the gnosis app
    df = pd.DataFrame(df)
    df["token_type"] = "erc20"
    df["id"] = pd.NA

    # build dataframe for airdrop and dump to csv
    airdrop = df[["token_type", "token_address", "receiver", "value", "id"]]
    airdrop.to_csv(
        "scripts/badger/topups/week_12.csv",
        index=False,
        header=["token_type", "token_address", "receiver", "value", "id"],
    )
    print(airdrop)
