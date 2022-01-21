from brownie import config
import requests
import pandas as pd

def main():
    wallet_address = ''
    scrape(wallet_address)

def scrape(address):
    with requests.session() as session:
        ethplorer_key = config['keys']['ETHPLORER_API_KEY']
        api_key = ethplorer_key if ethplorer_key else 'freekey'
        res = session.get(
            f'https://api.ethplorer.io/getAddressInfo/{address}?showETHTotals=false', 
            params={"apiKey": api_key}
            )
        assert res.status_code == 200

    token_data = {'token_address': [], 'value': []}
    for token in res.json()['tokens']:
        try:
            if int(token['tokenInfo']['decimals']) > 0:
                token_data['token_address'].append(token['tokenInfo']['address'])
                token_data['value'].append(token['rawBalance'])
        except KeyError:
            # Non-ERC20 token
            pass
        
    pd.DataFrame(token_data).to_csv(f'scripts/issue/23/{address}_token_balances.csv')
    