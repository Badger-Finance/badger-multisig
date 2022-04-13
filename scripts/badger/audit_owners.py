import requests
from json import JSONDecodeError

import pandas as pd
from rich.console import Console

from helpers.addresses import registry


GNOSIS_URLS  = {
    'eth': 'https://safe-transaction.gnosis.io',
    'bsc': 'https://safe-transaction.bsc.gnosis.io',
    'poly': 'https://safe-transaction.polygon.gnosis.io',
    'arbitrum': 'https://safe-transaction.arbitrum.gnosis.io',
    'ftm': 'https://safe.fantom.network'
}
C = Console()


def gnosis_api_call(address, chain='eth'):
    try:
        url = f'{GNOSIS_URLS[chain]}/api/v1/safes/{address}/'
        r = requests.get(url).json()
        return r
    except JSONDecodeError:
        pass


def label_in_address_book(addr):
    try:
        return next(
            k for k, v in registry.eth.badger_wallets.items() if v == addr
        )
    except StopIteration:
        return False


def main():
    # loop over multisigs
    data = []
    for chain in ['eth', 'bsc', 'poly', 'arbitrum', 'ftm']:
        for label, addr in registry[chain]['badger_wallets'].items():
            if not 'multisig' in label or 'test' in label:
                continue
            print(f'fetching {addr} from {GNOSIS_URLS[chain]}...', end='')
            r = gnosis_api_call(addr, chain)
            if r is None:
                C.print(' [red]FAIL[/red]')
                continue
            else:
                C.print('')
            # grab threshold and list of owners
            data.append({
                'address': addr,
                'chain': chain,
                'label': label,
                'threshold': r['threshold'],
                'owners': r['owners']
            })

    # build dataframe
    df = pd.DataFrame(data)
    df = df.set_index(['address', 'chain'])
    df = df.explode('owners')

    # map owner to label
    df['known_address'] = df['owners'].map(label_in_address_book)

    # map owner to category?

    # print and dump result
    print(df)
    df.to_csv('data/badger/audit_owners.csv')
