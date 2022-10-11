import pandas as pd
from brownie import interface
from decimal import Decimal

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    """
    build a gnosis airdrop csv with all topups needing to happen for a given
    week.
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    usdc = interface.ERC20(registry.eth.treasury_tokens.USDC, owner=safe)
    eurs = interface.ERC20(registry.eth.treasury_tokens.EURS, owner=safe)

    df = {"token_address": [], "receiver": [], "value": []}

    # https://github.com/Badger-Finance/badger-multisig/issues/191
    # send last bit of badger to deployer for bridging to arbi
    arbi_emissions_q1 = Decimal("1100.4016999999994")
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.badger_wallets.ops_deployer2)
    df["value"].append(arbi_emissions_q1)

    # https://github.com/Badger-Finance/badger-multisig/issues/196
    # add badger to the tree for weekly emissions
    week_9_badger_emissions = Decimal("35250.256355929996")
    week_9_rembadger_emissions = Decimal("7692.307692")
    catch_up_on_deficit = Decimal("0")  # still ~70k in the tree atm
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.badger_wallets.badgertree)
    df["value"].append(
        week_9_badger_emissions + week_9_rembadger_emissions + catch_up_on_deficit
    )

    # https://github.com/Badger-Finance/badger-multisig/issues/197
    # add digg to the tree for weekly emissions
    week_9_digg_emissions = Decimal("1.31")
    deficit = Decimal("3.8034617901343992")
    df["token_address"].append(registry.eth.treasury_tokens.DIGG)
    df["receiver"].append(registry.eth.badger_wallets.badgertree)
    df["value"].append(week_9_digg_emissions + deficit)

    # https://github.com/Badger-Finance/badger-multisig/issues/198
    # bi-weeky tx to remBADGER sett
    week_9_biweekly_transfer_rembadger = Decimal("11538.461538")
    df["token_address"].append(registry.eth.treasury_tokens.BADGER)
    df["receiver"].append(registry.eth.sett_vaults.remBADGER)
    df["value"].append(week_9_biweekly_transfer_rembadger)

    # https://github.com/Badger-Finance/badger-multisig/issues/205
    # lowest univ3 range has only been fulfilled partially
    # ppfs makes this calc not precise at all but there is enough dust in trops
    # to solve that
    missing_wbtc = Decimal("57.74") - Decimal("30.46831914")
    df["token_address"].append(registry.eth.sett_vaults.bcrvIbBTC)
    df["receiver"].append(registry.eth.badger_wallets.treasury_ops_multisig)
    df["value"].append(missing_wbtc)

    # clean usdc and eurs dust from 3eur farming
    dust_usdc = Decimal(usdc.balanceOf(safe)) / 10 ** usdc.decimals()
    df["token_address"].append(usdc.address)
    df["receiver"].append(registry.eth.badger_wallets.treasury_ops_multisig)
    df["value"].append(dust_usdc)
    dust_eurs = Decimal(eurs.balanceOf(safe)) / 10 ** eurs.decimals()
    df["token_address"].append(eurs.address)
    df["receiver"].append(registry.eth.badger_wallets.treasury_ops_multisig)
    df["value"].append(dust_eurs)

    # turn dict of lists into dataframe and add additional columns needed by
    # the gnosis app
    df = pd.DataFrame(df)
    df["token_type"] = "erc20"
    df["id"] = pd.NA

    # build dataframe for airdrop and dump to csv
    airdrop = df[["token_type", "token_address", "receiver", "value", "id"]]
    airdrop.to_csv(
        "scripts/badger/topups/week_9.csv",
        index=False,
        header=["token_type", "token_address", "receiver", "value", "id"],
    )
    print(airdrop)
