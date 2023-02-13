import os
import re
import requests
from contextlib import redirect_stdout
from datetime import datetime
from decimal import Decimal
from io import StringIO

import pandas as pd
from ape_safe import ApeSafe
from brownie import Contract, network, ETH_ADDRESS, exceptions, web3, chain
from eth_utils import is_address, to_checksum_address
from rich.console import Console
from rich.pretty import pprint
from tqdm import tqdm
from web3.exceptions import BadFunctionCallOutput

from great_ape_safe.ape_api import ape_apis
from helpers.chaindata import labels


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

        for class_name, cls in ape_apis.items():
            setattr(
                self,
                f"init_{class_name}",
                lambda *args, cn=class_name, c=cls, **kwargs: setattr(
                    self, cn, c(self, *args, **kwargs)
                ),
            )

    def take_snapshot(self, tokens):
        C.print(f"snapshotting {self.address}...")
        df = {"address": [], "symbol": [], "mantissa_before": [], "decimals": []}
        df["address"].append(ETH_ADDRESS)
        df["symbol"].append(labels[network.chain.id])
        df["mantissa_before"].append(Decimal(self.account.balance()))
        df["decimals"].append(Decimal(18))
        for token in tqdm(tokens):
            try:
                token = Contract(token) if type(token) != Contract else token
            except:
                token = (
                    Contract.from_explorer(token) if type(token) != Contract else token
                )
            if token.address not in df["address"]:
                try:
                    df["address"].append(token.address)
                    df["symbol"].append(token.symbol())
                    df["mantissa_before"].append(Decimal(token.balanceOf(self.address)))
                    df["decimals"].append(Decimal(token.decimals()))
                except Exception as e:
                    print(token, e)
        self.snapshot = pd.DataFrame(df)

    def print_snapshot(self, csv_destination=None):
        if not isinstance(self.snapshot, pd.DataFrame):
            return
        if self.snapshot is None:
            raise
        df = self.snapshot.set_index("address")
        for token in df.index.to_list():
            if token == ETH_ADDRESS:
                df.at[token, "mantissa_after"] = Decimal(self.account.balance())
            else:
                try:
                    token = Contract(token) if type(token) != Contract else token
                except:
                    token = (
                        Contract.from_explorer(token)
                        if type(token) != Contract
                        else token
                    )
                df.at[token.address, "mantissa_after"] = Decimal(token.balanceOf(self))

        # calc deltas
        df["balance_before"] = df["mantissa_before"] / 10 ** df["decimals"]
        df["balance_after"] = df["mantissa_after"] / 10 ** df["decimals"]
        df["balance_delta"] = (df["mantissa_after"] - df["mantissa_before"]) / 10 ** df[
            "decimals"
        ]

        # narrow down to columns of interest
        df = df.set_index("symbol")[
            ["balance_before", "balance_after", "balance_delta"]
        ]

        # only keep rows for which there is a delta
        df = df[df["balance_delta"] != 0]

        def locale_decimal(d):
            # format with thousands separator and 18 digits precision
            return "{0:,.18f}".format(d)

        if csv_destination:
            # grab only symbol & delta
            df_csv = pd.DataFrame(columns=["token", "claimable_amount"])
            df_csv["token"] = df.index
            df_csv["claimable_amount"] = df["balance_delta"].values
            df_csv.to_csv(
                csv_destination, index=False, header=["token", "claimable_amount"]
            )

        C.print(f"snapshot result for {self.address}:")
        C.print(
            df.to_string(formatters=[locale_decimal, locale_decimal, locale_decimal]),
            "\n",
        )

    def _set_safe_tx_gas(self, safe_tx, events, call_trace, reset, log_name, gas_coef):
        versions = safe_tx._safe_version.split(".")
        # safe_tx_gas is a hack for getting correct gas estimation in end user wallet's ui
        # but it is only needed on older versions of gnosis safes (<1.3.0)
        if int(versions[0]) <= 1 and int(versions[1]) < 3:
            receipt = self.preview(safe_tx, events, call_trace, reset)
            gas_used = receipt.gas_used
            safe_tx_gas = max(gas_used * 64 // 63, gas_used + 2500) + 500
            safe_tx.safe_tx_gas = 35_000 + int(gas_coef * safe_tx_gas)
            # as we are modifying the tx, previous signatures are not valid anymore
            safe_tx.signatures = b""
        else:
            receipt = self.preview(safe_tx, events, call_trace, reset)
            safe_tx.safe_tx_gas = 0
        if log_name:
            self._dump_log(safe_tx, receipt, log_name)
        return safe_tx, receipt

    def _dump_log(self, safe_tx, receipt, log_name):
        # logs .preview's events and call traces to log file, plus prettified
        # dict of the `safe_tx` and a safe's snapshot if it exists
        with redirect_stdout(StringIO()) as buffer:
            receipt.info()
            receipt.call_trace(True)
            pprint(safe_tx.__dict__)
            if hasattr(self, "snapshot"):
                self.print_snapshot()

        def remove_ansi_escapes(text):
            ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")
            return ansi_escape.sub("", text)

        os.makedirs("logs/", exist_ok=True)
        with open(
            f'logs/{datetime.now().strftime("%Y%m%d%H%M%S")}_{log_name}.log', "w"
        ) as f:
            f.write(remove_ansi_escapes(buffer.getvalue()))

    def post_safe_tx(
        self,
        skip_preview=False,
        events=True,
        call_trace=False,
        reset=True,
        silent=False,
        post=True,
        replace_nonce=None,
        log_name=None,
        csv_destination=None,
        gas_coef=1.5,
        safe_tx=None,
        tenderly=True,
        debank=False,
    ):
        # build a gnosis-py SafeTx object which can then be posted
        # skip_preview=True: skip preview **and with that also setting the gas**
        # events, call_trace and reset are params passed to .preview
        # silent=True: prevent printing of safe_tx attributes at end of run
        # post=True: make the actual live posting of the tx to the gnosis api
        if not safe_tx and replace_nonce:
            safe_tx = self.multisend_from_receipts(safe_nonce=replace_nonce)
        elif not safe_tx:
            safe_tx = self.multisend_from_receipts()
        if not skip_preview:
            safe_tx, receipt = self._set_safe_tx_gas(
                safe_tx, events, call_trace, reset, log_name, gas_coef
            )
        if tenderly:
            self._generate_tenderly_simulation(receipt, safe_tx.safe_tx_gas)
        if debank:
            self._debank_pre_execution(receipt, safe_tx.safe_tx_gas)
        if replace_nonce:
            safe_tx._safe_nonce = replace_nonce
        if not silent:
            pprint(safe_tx.__dict__)
        if hasattr(self, "snapshot"):
            self.print_snapshot(csv_destination)
        if post:
            self.post_transaction(safe_tx)

    def _get_safe_tx_by_nonce(self, safe_nonce):
        # retrieve SafeTx obj from pending transactions based on nonce
        pending = self.pending_transactions
        for safe_tx in pending:
            if safe_tx.safe_nonce == safe_nonce:
                return safe_tx
        raise  # didnt find safe_tx with corresponding nonce

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

    def contract(self, address, Interface=None, from_explorer=False):
        # instantiate a brownie contract, either from an interface, the
        # explorer or locally saved contract object. if address is somehow
        # invalid, return None.
        if is_address(address):
            address = to_checksum_address(address)
        else:
            try:
                address = web3.ens.resolve(address)
            except BadFunctionCallOutput:
                return None
        if not is_address(address):
            return None
        if Interface:
            return Interface(address, owner=self.account)
        elif from_explorer:
            return Contract.from_explorer(address, owner=self.account)
        else:
            return Contract(address, owner=self.account)

    def _generate_tenderly_simulation(self, receipt, gas):
        """
        docs: https://www.notion.so/Simulate-API-Documentation-6f7009fe6d1a48c999ffeb7941efc104
        """
        header = {
            "Content-Type": "application/json",
            "X-Access-Key": os.getenv("TENDERLY_ACCESS_KEY"),
        }
        api_url = f'https://api.tenderly.co/api/v1/account/{os.getenv("TENDERLY_USER")}/project/{os.getenv("TENDERLY_PROJECT")}/simulate'
        tx_payload = {
            "network_id": str(chain.id),
            "from": receipt.sender.address,
            "to": self.address,
            "input": receipt.input,
            "gas": 1_500_000 if gas == 0 else gas,
            "save": True,
            "save_if_fails": True,
            # storage ref: https://github.com/safe-global/safe-contracts/blob/main/contracts/libraries/SafeStorage.sol
            "state_objects": {self.address: {"storage": {"0x04": "0x01"}}},
        }
        r = requests.post(api_url, headers=header, json=tx_payload)
        r.raise_for_status()

        print(
            f"https://dashboard.tenderly.co/{os.getenv('TENDERLY_USER')}/{os.getenv('TENDERLY_PROJECT')}/simulator/{r.json()['simulation']['id']}"
        )

    def _debank_pre_execution(self, receipt, gas):
        """
        docs: https://docs.open.debank.com/en/reference/api-pro-reference/wallet#enhanced-transaction-pre-execution
        TransactionObject format: https://docs.open.debank.com/en/reference/api-models/transactionobject
        """
        header = {
            "content-type": "application/json",
            "AccessKey": os.getenv("DEBANK_API_KEY"),
        }
        api_url = "https://pro-openapi.debank.com/v1/wallet/pre_exec_tx"

        max_gas_fee = hex(int(2.1e10))
        tx_object = {
            "tx": {
                "chainId": chain.id,
                "from": receipt.sender.address,
                "to": self.address,
                "value": hex(receipt.value),
                "data": receipt.input,
                "gas": hex(1_500_000 if gas == 0 else gas),
                "maxFeePerGas": max_gas_fee,
                "maxPriorityFeePerGas": max_gas_fee,
                "nonce": hex(receipt.nonce),
            }
        }
        r = requests.post(
            api_url,
            headers=header,
            json=tx_object,
        )
        # TODO: it will revert with GS025 have not find a way
        # to by-pass: https://github.com/safe-global/safe-contracts/blob/main/contracts/Safe.sol#L282
        # since here the threshold storage variable cannot be override currently
        r.raise_for_status()
        print(r.json())
