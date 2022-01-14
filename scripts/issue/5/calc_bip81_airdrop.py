import pandas as pd


def main():
    # csv export of technical post mortem sheet:
    # https://docs.google.com/spreadsheets/d/1IPwk-_ZtZ3aIxaJgYm8wZ7W6biB65Ou46lkYnniAHzQ/edit#gid=168062083
    df = pd.read_csv(
        'scripts/issue/5/assets_stolen_recoverable-_transferFrom.csv',
    )

    # filter out victims for which funds have already been recovered
    recovered = df[df['type'] == 'recoverable']['victim']
    dff = df[~df['victim'].isin(recovered)].copy()

    # add the bibbtc token address
    dff['bibbtc_addr'] = '0xaE96fF08771a109dc6650a1BdCa62F2d558E40af'

    # sum up all value_wbtc left in the dataframe
    total_wbtc = dff['value_wbtc'].sum()

    # hardcoding total bibbtc tokens accrued by bip81 (with limited precision)
    total_bip81 = 198.98233981

    # calc initial restitution pro rata
    dff['pro_rata'] = dff['value_wbtc'] / total_wbtc * total_bip81
    assert dff['pro_rata'].sum() == total_bip81

    # build dataframe for airdrop;
    # filter on value > 0 and take only the necessary columns
    airdrop = dff[dff['pro_rata'] > 0][['bibbtc_addr', 'victim', 'pro_rata']]

    # dump df to csv for gnosis csv airdrop app
    airdrop.to_csv(
        'scripts/issue/5/airdrop_bip81.csv',
        index=False,
        header=['token_address', 'receiver', 'amount'],
    )
    print(airdrop)
    print(airdrop['pro_rata'].sum())
