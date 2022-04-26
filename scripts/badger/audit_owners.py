import requests
from json import JSONDecodeError

import pandas as pd
from rich.console import Console

from helpers.addresses import registry
from .audit_owners_mapper import roles


GNOSIS_URLS  = {
    'eth': 'https://safe-transaction.gnosis.io',
    'bsc': 'https://safe-transaction.bsc.gnosis.io',
    'poly': 'https://safe-transaction.polygon.gnosis.io',
    'arbitrum': 'https://safe-transaction.arbitrum.gnosis.io',
    'ftm': 'https://safe.fantom.network'
}
C = Console()


def gnosis_api_call(address, chain='eth'):
    url = f'{GNOSIS_URLS[chain]}/api/v1/safes/{address}/'
    return requests.get(url)


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
            if not (r.ok and r.status_code == 200):
                C.print(' [red]FAIL[/red]')
                continue
            C.print('')
            # grab threshold and list of owners
            data.append({
                'address': addr,
                'chain': chain,
                'label': label,
                'threshold': r.json()['threshold'],
                'owners': r.json()['owners']
            })

    # build dataframe
    df = pd.DataFrame(data)
    df = df.set_index(['address', 'chain'])
    df = df.explode('owners')

    # map owner to label
    df['public_label'] = df['owners'].map(label_in_address_book)

    # map owner to role
    df['owner_role'] = df['owners'].map(roles)

    # print and dump result
    print(df)
    df.to_csv('data/badger/audit_owners.csv')
