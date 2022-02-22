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
    df = {'token_address': [], 'receiver': [], 'value': []}

    # https://github.com/Badger-Finance/badger-multisig/issues/103
    # of 50k $bvecvx to add as tcl, we already added 24118650903987266519040
    still_to_add = Decimal('50_000e18') - Decimal('24118650903987266519040')
    df['token_address'].append(registry.eth.treasury_tokens.bveCVX)
    df['receiver'].append(
        registry.eth.badger_wallets.treasury_ops_multisig
    )
    df['value'].append(still_to_add / Decimal('1e18'))

    # https://github.com/Badger-Finance/badger-multisig/issues/109
    # deficit in tree for bcvxcrv is 145927.08293717116
    tree_bcvxcrv_deficit = Decimal('145928e18')
    bcvxcrv = interface.ISettV4h(
        registry.eth.sett_vaults.bcvxCRV, owner=safe.account
    )
    if bcvxcrv.balanceOf(safe) >= tree_bcvxcrv_deficit:
        topup = tree_bcvxcrv_deficit
    else:
        topup = bcvxcrv.balanceOf(safe)
    df['token_address'].append(bcvxcrv.address)
    df['receiver'].append(registry.eth.badger_wallets.badgertree)
    df['value'].append(topup / Decimal('1e18'))

    # https://github.com/Badger-Finance/badger-multisig/issues/118
    # https://github.com/Badger-Finance/badger-multisig/issues/136
    # add badger to the tree for weekly emissions:
    week_6_emissions = Decimal('33561.65978447947')
    week_7_emissions = Decimal('34565.28490125317')
    week_6_and_7_rembadger_emissions = Decimal('7692.307692') * 2
    tree_badger_deficit = Decimal('242_000') # roughly on 14th Feb
    catch_up_on_deficit = Decimal('50_000')
    df['token_address'].append(registry.eth.treasury_tokens.BADGER)
    df['receiver'].append(registry.eth.badger_wallets.badgertree)
    df['value'].append(
        week_6_emissions + week_7_emissions + week_6_and_7_rembadger_emissions + catch_up_on_deficit
    )

    # https://github.com/Badger-Finance/badger-multisig/issues/112
    # bi-weeky tx to remBADGER sett
    week_7_biweekly_transfer_rembadger = Decimal('11538.461538')
    df['token_address'].append(registry.eth.treasury_tokens.BADGER)
    df['receiver'].append(registry.eth.sett_vaults.remBADGER)
    df['value'].append(week_7_biweekly_transfer_rembadger)

    # https://github.com/Badger-Finance/badger-multisig/issues/154
    # techops fronted some badger for tree
    fronted = Decimal('6603.208250737497461487')
    df['token_address'].append(registry.eth.treasury_tokens.BADGER)
    df['receiver'].append(registry.eth.badger_wallets.techops_multisig)
    df['value'].append(fronted)

    # turn dict of lists into dataframe and add additional columns needed by
    # the gnosis app
    df = pd.DataFrame(df)
    df['token_type'] = 'erc20'
    df['id'] = pd.NA

    # build dataframe for airdrop and dump to csv
    airdrop = df[['token_type', 'token_address', 'receiver', 'value', 'id']]
    airdrop.to_csv(
        'scripts/badger/topups/week_6_and_7.csv',
        index=False,
        header=['token_type', 'token_address', 'receiver', 'value', 'id'],
    )
    print(airdrop)
