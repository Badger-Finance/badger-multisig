import json
import os
import requests
import sys
from decimal import Decimal
from pprint import pprint

from brownie import Contract, chain, interface, web3

from helpers.addresses import registry


class Cow():
    """
    docs: https://docs.cow.fi/
    explorer: https://explorer.cow.fi/
    api reference: https://api.cow.fi/docs/
    """


    def __init__(self, safe, prod=False):
        self.safe = safe
        self.prod = prod

        # contracts
        self.vault_relayer = self.safe.contract(registry.eth.cow.vault_relayer)
        # self.vault_relayer = interface.IGPv2VaultRelayer(
        #     registry.eth.cow.vault_relayer, owner=self.safe.account
        # )
        self.settlement = interface.IGPv2Settlement(
            registry.eth.cow.settlement, owner=self.safe.account
        )

        # determine api url based on current chain id and `prod` parameter
        chain_label = {
            1: 'mainnet',
            4: 'rinkeby',
            100: 'xdai'
        }
        prefix = 'https://api.cow.fi/' if prod else 'https://barn.api.cow.fi/'
        self.api_url = f'{prefix}{chain_label[chain.id]}/api/v1/'


    def _sell(self, sell_token, mantissa_sell, buy_token,
        mantissa_buy, deadline, coef=1):
        """call api to get sell quote and post order"""

        # make sure mantissa is an integer
        assert type(mantissa_sell) == int

        # get the fee and exact amount to buy after fee
        fee_and_quote_payload = {
            'sellToken': sell_token.address,
            'buyToken': buy_token.address,
            'sellAmountBeforeFee': mantissa_sell
        }
        print('FEE AND QUOTE PAYLOAD:')
        pprint(fee_and_quote_payload)
        print('')

        r = requests.get(self.api_url+'feeAndQuote/sell', params=fee_and_quote_payload)
        print('FEE AND QUOTE RESPONSE:')
        pprint(r.json())
        print('')
        assert r.ok and r.status_code == 200

        # grab values needed to post the order to the api
        fee_amount = int(r.json()['fee']['amount'])
        if mantissa_buy:
            # overwrite quote in case order has a limit
            assert type(mantissa_buy) == int
            buy_amount_after_fee = mantissa_buy
        else:
            buy_amount_after_fee = int(int(r.json()['buyAmountAfterFee']) * coef)
        assert fee_amount > 0
        assert buy_amount_after_fee > 0

        # add deadline to current block timestamp
        deadline = chain.time() + deadline

        # submit order
        order_payload = {
            'sellToken': sell_token.address,
            'buyToken': buy_token.address,
            'receiver': self.safe.address,
            'sellAmount': str(mantissa_sell - fee_amount),
            'buyAmount': str(buy_amount_after_fee),
            'validTo': deadline,
            'appData': web3.keccak(text='great_ape_safe').hex(),
            'feeAmount': str(fee_amount),
            'kind': 'sell',
            'partiallyFillable': False,
            'sellTokenBalance': 'erc20',
            'buyTokenBalance': 'erc20',
            'signingScheme': 'presign',
            'signature': self.safe.address,
            'from': self.safe.address,
        }
        print('ORDER PAYLOAD')
        pprint(order_payload)
        print('')

        r = requests.post(f'{self.api_url}orders', json=order_payload)
        order_uid = r.json()
        print('ORDER RESPONSE')
        pprint(order_uid)
        print('')
        assert r.ok and r.status_code == 201

        # dump order to json and add staging label if necessary
        path = 'logs/trading/prod/' if self.prod else 'logs/trading/staging/'
        os.makedirs(path, exist_ok=True)
        with open(f'{path}{order_uid}.json', 'w+') as f:
            f.write(json.dumps(order_payload))

        # pre-approve the order on-chain, as set by `signingScheme`: presign
        # (otherwise signature would go in api order payload)
        # https://docs.cow.fi/smart-contracts/settlement-contract/signature-schemes
        self.settlement.setPreSignature(order_uid, True)


    def allow_relayer(self, asset, mantissa):
        """
        make sure vault relayer is approved to transferFrom the asset and
        the amount to be sold
        """
        allowance = asset.allowance(
            self.safe,
            self.vault_relayer
        )
        if allowance < mantissa:
            asset.approve(self.vault_relayer, mantissa)
            assert asset.allowance(self.safe, self.vault_relayer) >= mantissa
            print('approval needs to be executed on-chain before order can be posted to api!\n')
            self.safe.post_safe_tx()
            sys.exit()


    def market_sell(self, asset_sell, asset_buy, mantissa_sell, deadline=60*60, chunks=1, coef=1):
        """
        wrapper for _sell method;
        mantissa_sell is exact and order is submitted at quoted rate
        """
        assert type(chunks) == int
        self.allow_relayer(asset_sell, mantissa_sell)
        mantissa_sell = int(Decimal(mantissa_sell) / chunks)
        for n in range(chunks):
            self._sell(
                asset_sell,
                mantissa_sell,
                asset_buy,
                mantissa_buy=None,
                # without + n api will raise DuplicateOrder when chunks > 1
                deadline=deadline + n,
                coef=coef
            )


    def limit_sell(self, asset_sell, asset_buy, mantissa_sell, mantissa_buy, deadline=60*60, chunks=1):
        """
        wrapper for _sell method;
        both the sell and buy mantissas are exact, resulting in a limit order
        """
        assert type(chunks) == int
        self.allow_relayer(asset_sell, mantissa_sell)
        mantissa_sell = int(Decimal(mantissa_sell) / chunks)
        mantissa_buy = int(Decimal(mantissa_buy) / chunks)
        for n in range(chunks):
            self._sell(
                asset_sell,
                mantissa_sell,
                asset_buy,
                mantissa_buy,
                # without + n api will raise DuplicateOrder when chunks > 1
                deadline + n
            )


    def cancel_order(self, order_uid):
        self.settlement.invalidateOrder(order_uid)
