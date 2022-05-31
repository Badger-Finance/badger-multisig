import os
import re
from contextlib import redirect_stdout
from datetime import datetime
from decimal import Decimal
from io import StringIO

import pandas as pd
from ape_safe import ApeSafe
from brownie import Contract, network, ETH_ADDRESS, exceptions
from rich.console import Console
from rich.pretty import pprint
from tqdm import tqdm
from helpers.chaindata import labels

from great_ape_safe.ape_api.aave import Aave
from great_ape_safe.ape_api.anyswap import Anyswap
from great_ape_safe.ape_api.badger import Badger
from great_ape_safe.ape_api.balancer import Balancer
from great_ape_safe.ape_api.compound import Compound
from great_ape_safe.ape_api.convex import Convex
from great_ape_safe.ape_api.cow import Cow
from great_ape_safe.ape_api.curve import Curve
from great_ape_safe.ape_api.curve_v2 import CurveV2
from great_ape_safe.ape_api.opolis import Opolis
from great_ape_safe.ape_api.pancakeswap_v2 import PancakeswapV2
from great_ape_safe.ape_api.rari import Rari
from great_ape_safe.ape_api.solidly import Solidly
from great_ape_safe.ape_api.spookyswap import SpookySwap
from great_ape_safe.ape_api.sushi import Sushi
from great_ape_safe.ape_api.uni_v2 import UniV2
from great_ape_safe.ape_api.uni_v3 import UniV3


C = Console()


class GreatApeSafe(ApeSafe):
    """
    Child of ApeSafe object, with added functionalities:
    - contains a limited library of functions needed to ape in and out of known
      defi platforms (aave, compound, convex, curve)
    - wrapper functions for setting (limit) orders on the cowswap protocol
    - can take a snapshot of its starting and ending balances and print the
      difference
    - one single function to estimate gas correctly (for both gnosis safe
      versions before and after v1.3.0) and post tx to gnosis api
    """


    def __init__(self, address, base_url=None, multisend=None):
        super().__init__(address, base_url, multisend)


    def init_all(self):
        for method in self.__dir__():
            if method.startswith('init_') and method != 'init_all':
                try:
                    getattr(self, method)()
                except exceptions.ContractNotFound:
                    # different chain
                    pass


    def init_aave(self):
        self.aave = Aave(self)


    def init_anyswap(self):
        self.anyswap = Anyswap(self)


    def init_badger(self):
        self.badger = Badger(self)


    def init_balancer(self):
        self.balancer = Balancer(self)


    def init_compound(self):
        self.compound = Compound(self)


    def init_convex(self):
        self.convex = Convex(self)


    def init_cow(self, prod=False):
        self.cow = Cow(self, prod)


    def init_curve(self):
        self.curve = Curve(self)


    def init_curve_v2(self):
        self.curve_v2 = CurveV2(self)


    def init_opolis(self):
        self.opolis = Opolis(self)


    def init_pancakeswap_v2(self):
        self.pancakeswap_v2 = PancakeswapV2(self)


    def init_rari(self):
        self.rari = Rari(self)


    def init_solidly(self):
        self.solidly = Solidly(self)


    def init_spookyswap(self):
        self.spookyswap = SpookySwap(self)


    def init_sushi(self):
        self.sushi = Sushi(self)


    def init_uni_v2(self):
        self.uni_v2 = UniV2(self)


    def init_uni_v3(self):
        self.uni_v3 = UniV3(self)


    def take_snapshot(self, tokens):
        C.print(f'snapshotting {self.address}...')
        df = {'address': [], 'symbol': [], 'mantissa_before': [], 'decimals': []}
        df['address'].append(ETH_ADDRESS)
        df['symbol'].append(labels[network.chain.id])
        df['mantissa_before'].append(Decimal(self.account.balance()))
        df['decimals'].append(Decimal(18))
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


    def print_snapshot(self, csv_destination=None):
        if self.snapshot is None:
            raise
        df = self.snapshot.set_index('address')
        for token in df.index.to_list():
            if token == ETH_ADDRESS:
                df.at[token, 'mantissa_after'] = Decimal(self.account.balance())
            else:
                try:
                    token = Contract(token) if type(token) != Contract else token
                except:
                    token = Contract.from_explorer(token) if type(token) != Contract else token
                df.at[token.address, 'mantissa_after'] = Decimal(token.balanceOf(self))

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

        if csv_destination:
            # grab only symbol & delta
            df_csv = pd.DataFrame(columns=["token", "claimable_amount"])
            df_csv["token"] = df.index
            df_csv["claimable_amount"] = df['balance_delta'].values
            df_csv.to_csv(
                csv_destination,
                index=False,
                header=["token", "claimable_amount"]
            )

        C.print(f'snapshot result for {self.address}:')
        C.print(df.to_string(formatters=[locale_decimal, locale_decimal, locale_decimal]), '\n')


    def _set_safe_tx_gas(self, safe_tx, events, call_trace, reset, log_name, gas_coef):
        versions = safe_tx._safe_version.split('.')
        # safe_tx_gas is a hack for getting correct gas estimation in end user wallet's ui
        # but it is only needed on older versions of gnosis safes (<1.3.0)
        if int(versions[0]) <= 1 and int(versions[1]) < 3:
            receipt = self.preview(safe_tx, events, call_trace, reset)
            gas_used = receipt.gas_used
            safe_tx_gas = max(gas_used * 64 // 63, gas_used + 2500) + 500
            safe_tx.safe_tx_gas = 35_000 + int(gas_coef * safe_tx_gas)
            # as we are modifying the tx, previous signatures are not valid anymore
            safe_tx.signatures = b''
        else:
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


    def post_safe_tx(self, skip_preview=False, events=True, call_trace=False, reset=True, silent=False, post=True, replace_nonce=None, log_name=None, csv_destination=None, gas_coef=1.5, safe_tx=None):
        # build a gnosis-py SafeTx object which can then be posted
        # skip_preview=True: skip preview **and with that also setting the gas**
        # events, call_trace and reset are params passed to .preview
        # silent=True: prevent printing of safe_tx attributes at end of run
        # post=True: make the actual live posting of the tx to the gnosis api
        if safe_tx_arg:
            safe_tx = safe_tx_arg
        else:
            safe_tx = self.multisend_from_receipts()
        if not skip_preview:
            safe_tx = self._set_safe_tx_gas(safe_tx, events, call_trace, reset, log_name, gas_coef)
        if replace_nonce:
            safe_tx._safe_nonce = replace_nonce
        if not silent:
            pprint(safe_tx.__dict__)
        if hasattr(self, 'snapshot'):
            self.print_snapshot(csv_destination)
        if post:
            self.post_transaction(safe_tx)


    def _get_safe_tx_by_nonce(self, safe_nonce):
        # retrieve SafeTx obj from pending transactions based on nonce
        pending = self.pending_transactions
        for safe_tx in pending:
            if safe_tx.safe_nonce == safe_nonce:
                return safe_tx
        raise # didnt find safe_tx with corresponding nonce


    def sign_with_frame_hardware_wallet(self, safe_tx_nonce=None):
        # allows signing a SafeTx object with hardware wallet
        # posts the signature to gnosis endpoint
        if safe_tx_nonce:
            safe_tx = self._get_safe_tx_by_nonce(safe_tx_nonce)
        else:
            safe_tx = self.pending_transactions[0]
        pprint(safe_tx.__dict__)
        signature = self.sign_with_frame(safe_tx)
        self.post_signature(safe_tx, signature)


    def execute_with_frame_hardware_wallet(self, safe_tx_nonce=None):
        # executes fully signed tx with frame thru hardware wallet
        if safe_tx_nonce:
            safe_tx = self._get_safe_tx_by_nonce(safe_tx_nonce)
        else:
            safe_tx = self.pending_transactions[0]
        pprint(safe_tx.__dict__)
        self.execute_transaction_with_frame(safe_tx)
