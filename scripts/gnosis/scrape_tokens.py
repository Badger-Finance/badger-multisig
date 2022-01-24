from brownie import interface
import os
import pandas as pd
from helpers.addresses import registry
from decimal import Decimal
from rich.console import Console
from rich.progress import Progress
from rich.table import Table


console = Console()


def main():
    """
    generate a csv airdrop of all tokens and their balances from `treasurey_tokens` for a given address
    csv saved to scripts/gnosos/results/<address>_token_balances.csv
    
    `scrape` can be called directly from command line with an address:
    brownie run scrape_tokens.py scrape <address> <receiver>
    """
    
    wallet_address = ''
    receiver=''
    scrape(wallet_address, receiver)

def scrape(address, receiver=''):
    with Progress() as progress:
        token_data = {'token_type': [], 'token_address': [], 'receiver': [], 'value': [], 'id': [], 'decimals': []}
        
        scraping = progress.add_task("[yellow]Scraping...", total=len(registry.eth.treasury_tokens))
        table = Table()
        
        for key in token_data:
            table.add_column(key, justify="right", style="bright_yellow")
            
        for token_name in registry.eth.treasury_tokens:
            token = interface.ERC20(registry.eth.treasury_tokens[token_name])
            decimals = token.decimals()
            bal = token.balanceOf(address)
            bal_ether = bal / Decimal(10 ** decimals)
            
            if bal > 0:
                token_data['token_type'].append('erc20')
                token_data['token_address'].append(token.address)
                token_data['receiver'].append(receiver)
                token_data['value'].append(bal_ether)
                token_data['id'].append('')
                # required if not part of uniswap token list - https://github.com/bh2smith/safe-airdrop#loading-the-app-in-gnosis-safe-interface
                token_data['decimals'].append(decimals)
                
                table.add_row("erc20", token.name(), receiver, str(bal_ether), '', str(decimals))
                
            progress.update(scraping, advance=1)
        
    console.print(table)
    pd.DataFrame(token_data).to_csv(f'{os.getcwd()}/scripts/gnosis/results/{address}_token_balances.csv', index=False)
