import os
import re
from contextlib import redirect_stdout
from datetime import datetime
from decimal import Decimal
from io import StringIO

import pandas as pd
from ape_safe import ApeSafe
from brownie import Contract, web3
from rich.console import Console
from rich.pretty import pprint
from tqdm import tqdm

from great_ape_safe.api_safe.aave import Aave
from great_ape_safe.api_safe.compound import Compound
from great_ape_safe.api_safe.convex import Convex
from great_ape_safe.api_safe.curve import Curve
from great_ape_safe.api_safe.opolis import Opolis


C = Console()


class GreatApeSafe(ApeSafe):
    """
    Child of ApeSafe object, with added functionalities:
    - contains a limited library of functions needed to ape in and out of known
      defi platforms (aave, compound, convex, curve)
    - can take a snapshot of its starting and ending balances and print the
      difference
    - one single function to estimate gas correctly (for both gnosis safe
      versions before and after v1.3.0) and post tx to gnosis api
    """


    def __init__(self, address, base_url=None, multisend=None):
        super().__init__(address, base_url=None, multisend=None)


    def init_all(self):
        self.init_aave()
        self.init_compound()
        self.init_convex()
        self.init_curve()
        self.init_opolis()
        

    def init_aave(self):
        self.aave = Aave(self)


    def init_compound(self):
        self.compound = Compound(self)


    def init_convex(self):
        self.convex = Convex(self)


    def init_curve(self):
        self.curve = Curve(self)
    
    def init_opolis(self):
        self.opolis = Opolis(self)


    def take_snapshot(self, tokens):
        C.print(f'snapshotting {self.address}...')
        df = {'address': [], 'symbol': [], 'mantissa_before': [], 'decimals': []}
        df['address'].append('0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')
        df['symbol'].append('ETH')
        df['mantissa_before'].append(Decimal(self.account.balance()))
        df['decimals'].append(18)
        for token in tqdm(tokens):
            try:
                token = Contract(token) if type(token) != Contract else token
            except:
                token = Contract.from_explorer(token) if type(token) != Contract else token
            if token.address not in df['address']:
                df['address'].append(token.address)
                df['symbol'].append(token.symbol())
                df['mantissa_before'].append(Decimal(token.balanceOf(self.address)))
                df['decimals'].append(Decimal(token.decimals()))
        self.snapshot = pd.DataFrame(df)


    def print_snapshot(self):
        if self.snapshot is None:
            raise
        df = self.snapshot.set_index('address')
        for token in df.index.to_list():
            if token == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
                df.at[token, 'mantissa_after'] = Decimal(self.account.balance())
            else:
                df.at[token, 'mantissa_after'] = Decimal(Contract(token).balanceOf(self))

        # calc deltas
        df['balance_before'] = df['mantissa_before'] / 10 ** df['decimals']
        df['balance_after'] = df['mantissa_after']  / 10 ** df['decimals']
        df['balance_delta'] = (df['mantissa_after'] - df['mantissa_before']) / 10 ** df['decimals']

        # narrow down to columns of interest
        df = df.set_index('symbol')[['balance_before', 'balance_after', 'balance_delta']]

        # only keep rows for which there is a delta
        df = df[df['balance_delta'] != 0]

        def locale_decimal(d):
            # format with thousands separator and 18 digits precision
            return '{0:,.18f}'.format(d)

        C.print(f'snapshot result for {self.address}:')
        C.print(df.to_string(formatters=[locale_decimal, locale_decimal, locale_decimal]), '\n')


    def _set_safe_tx_gas(self, safe_tx, events, call_trace, reset, log_name):
        versions = safe_tx._safe_version.split('.')
        # safe_tx_gas is a hack for getting correct gas estimation in end user wallet's ui
        # but it is only needed on older versions of gnosis safes (<1.3.0)
        if int(versions[0]) <= 1 and int(versions[1]) < 3:
            receipt = self.preview(safe_tx, events, call_trace, reset)
            gas_used = receipt.gas_used
            safe_tx_gas = max(gas_used * 64 // 63, gas_used + 2500) + 500
            safe_tx.safe_tx_gas = 35_000 + int(1.5 * safe_tx_gas)
            # as we are modifying the tx, previous signatures are not valid anymore
            safe_tx.signatures = b''
        else:
            safe_tx.safe_tx_gas = int(web3.eth.getBlock('latest').gasLimit * .8)
            receipt = self.preview(safe_tx, events, call_trace, reset)
            safe_tx.safe_tx_gas = 0
        if log_name:
            self._dump_log(safe_tx, receipt, log_name)
        return safe_tx


    def _dump_log(self, safe_tx, receipt, log_name):
        # logs .preview's events and call traces to log file, plus prettified
        # dict of the `safe_tx` and a safe's snapshot if it exists
        with redirect_stdout(StringIO()) as buffer:
            receipt.info()
            receipt.call_trace(True)
            pprint(safe_tx.__dict__)
            if hasattr(self, 'snapshot'):
                self.print_snapshot()

        def remove_ansi_escapes(text):
            ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
            return ansi_escape.sub('', text)

        os.makedirs('logs/', exist_ok=True)
        with open(f'logs/{datetime.now().strftime("%Y%m%d%H%M%S")}_{log_name}.log', 'w') as f:
            f.write(remove_ansi_escapes(buffer.getvalue()))


    def post_safe_tx(self, skip_preview=False, events=True, call_trace=False, reset=True, silent=False, post=True, log_name=None):
        # build a gnosis-py SafeTx object which can then be posted
        # skip_preview=True: skip preview **and with that also setting the gas**
        # events, call_trace and reset are params passed to .preview
        # silent=True: prevent printing of safe_tx attributes at end of run
        # post=True: make the actual live posting of the tx to the gnosis api
        safe_tx = self.multisend_from_receipts()
        if not skip_preview:
            safe_tx = self._set_safe_tx_gas(safe_tx, events, call_trace, reset, log_name)
        if not silent:
            pprint(safe_tx.__dict__)
        if hasattr(self, 'snapshot'):
            self.print_snapshot()
        if post:
            self.post_transaction(safe_tx)
