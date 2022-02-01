from decimal import Decimal, getcontext

import pandas as pd

from helpers.addresses import registry


# maximum precision of google sheets
# https://stackoverflow.com/a/44534232/1838257
getcontext().prec = 15


def main():
    # csv export of technical post mortem sheet:
    # https://docs.google.com/spreadsheets/d/1IPwk-_ZtZ3aIxaJgYm8wZ7W6biB65Ou46lkYnniAHzQ/edit#gid=168062083
    df = pd.read_csv(
        'scripts/issue/5/assets_stolen_recoverable-_transferFrom.csv',
        converters={'value_wbtc': Decimal, 'value_usd_2dec': Decimal},
    )

    # filter out victims for which funds have already been recovered
    recovered = df[df['type'] == 'recoverable']['victim']
    dff = df[~df['victim'].isin(recovered)].copy()

    wbtc_rate = dff.at[1, 'value_usd_2dec'] / dff.at[1, 'value_wbtc']

    # exception: convert $cvx value of single row to wbtc
    cvx_idx = dff[dff['value_cvx'] > 0].index
    dff.at[cvx_idx, 'value_wbtc'] = dff['value_usd_2dec'] / wbtc_rate

    # exception: convert $weth value of single row to wbtc
    eth_idx = dff[dff['value_weth'] > 0].index
    dff.at[eth_idx, 'value_wbtc'] = dff['value_usd_2dec'] / 2 / wbtc_rate

    # sum up all value_wbtc in the current dataframe
    total_wbtc = Decimal(dff['value_wbtc'].sum())

    # hardcoding total rembadger tokens minted
    total_rembadger = 2000

    # calc initial restitution pro rata
    dff['rembadger'] = dff['value_wbtc'] / total_wbtc * total_rembadger
    assert dff['rembadger'].sum() == total_rembadger

    # add the $rembadger token address and other gnosis airdrop app columns
    dff['token_type'] = 'erc20'
    dff['token_addr'] = registry.eth.sett_vaults.remBADGER
    dff['id'] = pd.NA

    # build dataframe for airdrop;
    # filter on value > 0 and take only the necessary columns
    airdrop = dff[dff['rembadger'] > 0][
        ['token_type', 'token_addr', 'victim', 'rembadger', 'id']
    ]

    # dump df to csv for gnosis csv airdrop app
    airdrop.to_csv(
        'scripts/issue/69/airdrop_rembadger.csv',
        index=False,
        header=['token_type', 'token_address', 'receiver', 'value', 'id'],
    )
    print(airdrop)
    print(airdrop['rembadger'].sum())
