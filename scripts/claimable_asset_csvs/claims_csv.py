import datetime
import os
import pandas as pd

from brownie import chain

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

# we could add tokens here following up new treasury positions
tokens_claimed = [
    registry.eth.treasury_tokens.AAVE,  # aave collateral
    registry.eth.treasury_tokens.stkAAVE,
    registry.eth.treasury_tokens.CVX,  # convex lp
    registry.eth.treasury_tokens.CRV,
    registry.eth.treasury_tokens.bcvxCRV,  # tree
    registry.eth.treasury_tokens.bveCVX,
    registry.eth.treasury_tokens.bCVX,
    registry.eth.treasury_tokens.BADGER,  # univ3
    registry.eth.treasury_tokens.WBTC,
]


def main(json_file_name=None):
    if not json_file_name:
        json_file_path = None
    else:
        json_file_path = f"{os.path.dirname(__file__)}/tree_jsons/{json_file_name}"

    # main msigs with positions earning or with pendant claimable assets
    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    dev = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)

    vault.take_snapshot(tokens_claimed)
    dev.take_snapshot(tokens_claimed)

    block_height = chain[-1].number

    # convex chunk
    vault.init_convex()
    vault.convex.claim_all()

    # univ3 chunk
    vault.init_uni_v3()
    vault.uni_v3.collect_fees()

    # aave chunk
    vault.init_aave()
    vault.aave.claim_all(markets=[registry.eth.treasury_tokens.aUSDC])

    # badger chunk
    vault.init_badger()
    vault.badger.claim_all(json_file_path)
    dev.init_badger()
    dev.badger.claim_all(json_file_path)

    # generate csv files with deltas at run time
    vault.print_snapshot(
        csv_destination=f"scripts/claimable_asset_csvs/claimable_snap/claimable_assets_{vault.address}_{datetime.date.today()}_block_{block_height}.csv",
    )
    dev.print_snapshot(
        csv_destination=f"scripts/claimable_asset_csvs/claimable_snap/claimable_assets_{dev.address}_{datetime.date.today()}_block_{block_height}.csv"
    )


def csv_diff(address=None, date=None, block_ref=None, block_against=None):
    latest_csv = pd.read_csv(
        f"{os.path.dirname(__file__)}/claimable_snap/claimable_assets_{address}_{date}_block_{block_ref}.csv"
    )

    oldest_csv = pd.read_csv(
        f"{os.path.dirname(__file__)}/claimable_snap/claimable_assets_{address}_{date}_block_{block_against}.csv"
    )

    diff_csv = latest_csv.set_index("token").subtract(oldest_csv.set_index("token"))

    diff_csv.to_csv(
        f"{os.path.dirname(__file__)}/trailing_claimable_revenue/{address}_from_block_{block_against}_to_block_{block_ref}.csv"
    )
