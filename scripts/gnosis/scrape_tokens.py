from brownie import Contract
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
    csv saved to scripts/gnosis/<address>_token_balances.csv

    `scrape` can be called directly from command line with an address:
    brownie run scrape_tokens.py scrape <address> <receiver>
    """

    wallet_address = ''
    receiver=''
    scrape(wallet_address, receiver)

def scrape(address, receiver=''):
    with Progress() as progress:
        token_set = set(list(registry.eth.treasury_tokens.values()) + \
            list(registry.eth.sett_vaults.values()) + \
            list(registry.eth.rari.values()))
        token_data = {'token_type': [], 'token_address': [], 'receiver': [], 'value': [], 'id': []}

        scraping = progress.add_task("[yellow]Scraping...", total=len(token_set))
        table = Table()

        for key in token_data:
            table.add_column(key, justify="right", style="bright_yellow")

        for token_addr in token_set:
            if token_addr in [registry.eth.rari.dai_manager, registry.eth.rari.unitroller]:
                continue
            token = Contract(token_addr)
            bal = token.balanceOf(address)
            bal_ether = bal / Decimal(10 ** token.decimals())

            if bal > 0:
                token_data['token_type'].append('erc20')
                token_data['token_address'].append(token.address)
                token_data['receiver'].append(receiver)
                token_data['value'].append(bal_ether)
                token_data['id'].append('')
                # required if not part of uniswap token list - https://github.com/bh2smith/safe-airdrop#loading-the-app-in-gnosis-safe-interface

                table.add_row("erc20", token.name(), receiver, str(bal_ether), '')

            progress.update(scraping, advance=1)

    console.print(table)
    pd.DataFrame(token_data).to_csv(f'{os.getcwd()}/scripts/gnosis/{address}_token_balances.csv', index=False)
    console.print(f"[bold green]scripts/gnosis/{address}_token_balances.csv")
