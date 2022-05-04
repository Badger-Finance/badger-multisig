
import pandas as pd
from decimal import Decimal

from helpers.addresses import registry


def main():
    df = {"token_address": [], "receiver": [], "value": []}

    # https://github.com/Badger-Finance/badger-multisig/issues/311#issuecomment-1108524915
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.badger_wallets.treasury_ops_multisig)
    df["value"].append(Decimal('150_000'))

    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.drippers.rembadger_2022_q2)
    df["value"].append(Decimal('51_913.076921'))

    df = pd.DataFrame(df)
    df["token_type"] = "erc20"
    df["id"] = pd.NA

    # build dataframe for airdrop and dump to csv
    airdrop = df[["token_type", "token_address", "receiver", "value", "id"]]
    airdrop.to_csv(
        "scripts/issue/311/month_5.csv",
        index=False,
        header=["token_type", "token_address", "receiver", "value", "id"],
    )
    print(airdrop)



from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    tree = GreatApeSafe(registry.eth.badger_wallets.badgertree)
    dripper = GreatApeSafe(registry.eth.drippers.rembadger_2022_q2)

    badger = interface.ERC20(
        registry.eth.treasury_tokens.BADGER, owner=safe.account
    )

    safe.take_snapshot([badger])
    tree.take_snapshot([badger])
    dripper.take_snapshot([badger])

    badger.transfer(tree, 150_000e18)
    badger.transfer(dripper, Decimal(51_913.076921) * Decimal(1e18))

    safe.print_snapshot()
    tree.print_snapshot()
    dripper.print_snapshot()

    safe.post_safe_tx()
