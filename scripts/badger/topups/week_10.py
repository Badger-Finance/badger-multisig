import pandas as pd
from decimal import Decimal

from helpers.addresses import registry


def main():
    """
    build a gnosis airdrop csv with all topups needing to happen for a given
    week.
    """

    df = {"token_address": [], "receiver": [], "value": []}

    # https://github.com/Badger-Finance/badger-multisig/issues/230
    # add badger to the tree for weekly emissions
    week_10_badger_emissions = Decimal("36944.415301991816")
    week_10_rembadger_emissions = Decimal("7692.307692")
    catch_up_on_deficit = Decimal("0")  # still ~44k in the tree atm
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.badger_wallets.badgertree)
    df["value"].append(
        week_10_badger_emissions + week_10_rembadger_emissions + catch_up_on_deficit
    )

    # https://github.com/Badger-Finance/badger-multisig/issues/234
    # send funds to treasury ops
    relief_vault_badger_emissions_task = 90000
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.badger_wallets.treasury_ops_multisig)
    df["value"].append(relief_vault_badger_emissions_task)

    # turn dict of lists into dataframe and add additional columns needed by
    # the gnosis app
    df = pd.DataFrame(df)
    df["token_type"] = "erc20"
    df["id"] = pd.NA

    # build dataframe for airdrop and dump to csv
    airdrop = df[["token_type", "token_address", "receiver", "value", "id"]]
    airdrop.to_csv(
        "scripts/badger/topups/week_10.csv",
        index=False,
        header=["token_type", "token_address", "receiver", "value", "id"],
    )
    print(airdrop)
