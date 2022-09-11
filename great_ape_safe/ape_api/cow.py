import json
import os
import requests
import sys
from decimal import Decimal
from pprint import pprint

from brownie import chain, interface, web3
from rich.prompt import Confirm

from helpers.addresses import registry


class Cow:
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
        chain_label = {1: "mainnet", 4: "rinkeby", 100: "xdai"}
        prefix = "https://api.cow.fi/" if prod else "https://barn.api.cow.fi/"
        self.api_url = f"{prefix}{chain_label[chain.id]}/api/v1/"

    def get_fee_and_quote(self, sell_token, buy_token, mantissa_sell):
        # make sure mantissa is an integer
        mantissa_sell = int(mantissa_sell)

        # get the fee and exact amount to buy after fee
        fee_and_quote_payload = {
            "sellToken": sell_token.address,
            "buyToken": buy_token.address,
            "sellAmountBeforeFee": mantissa_sell,
        }
        print("FEE AND QUOTE PAYLOAD:")
        pprint(fee_and_quote_payload)
        print("")

        r = requests.get(
            self.api_url + "feeAndQuote/sell", params=fee_and_quote_payload
        )
        print("FEE AND QUOTE RESPONSE:")
        pprint(r.json())
        print("")
        assert r.ok and r.status_code == 200

        return r.json()

    def _sell(
        self,
        sell_token,
        mantissa_sell,
        buy_token,
        mantissa_buy,
        deadline,
        coef,
        destination,
        origin,
    ):
        """call api to get sell quote and post order"""

        # set destination to self if not specified
        destination = self.safe.address if not destination else destination

        # make sure mantissa is an integer
        mantissa_sell = int(mantissa_sell)

        # get the fee and exact amount to buy after fee
        fee_and_quote = self.get_fee_and_quote(sell_token, buy_token, mantissa_sell)

        # grab values needed to post the order to the api
        fee_amount = int(fee_and_quote["fee"]["amount"])
        if mantissa_buy:
            # overwrite quote in case order has a limit
            mantissa_buy = int(mantissa_buy)
            buy_amount_after_fee = mantissa_buy
        else:
            buy_amount_after_fee = int(int(fee_and_quote["buyAmountAfterFee"]) * coef)
            pricer = interface.IOnChainPricing(
                interface.IBribesProcessor(registry.eth.cvx_bribes_processor).pricer(),
                owner=self.safe.account,
            )
            naive_quote = pricer.findOptimalSwap(sell_token, buy_token, mantissa_sell)
            if naive_quote[1] > buy_amount_after_fee:
                # manual sanity check whether onchain quote is acceptable
                override = Confirm.ask(
                    f"""cowswap quotes:\t{mantissa_sell / 10**sell_token.decimals()} {sell_token.symbol()} for {buy_amount_after_fee / 10**buy_token.decimals()} {buy_token.symbol()}
{naive_quote[0]} quotes:\t{mantissa_sell / 10**sell_token.decimals()} {sell_token.symbol()} for {naive_quote[1] / 10**buy_token.decimals()} {buy_token.symbol()}
pass {naive_quote[0]}'s quote to cowswap instead?"""
                )
                if override:
                    buy_amount_after_fee = naive_quote[1]
        assert fee_amount > 0
        assert buy_amount_after_fee > 0

        # add deadline to current block timestamp
        deadline = chain.time() + deadline

        # submit order
        order_payload = {
            "sellToken": sell_token.address,
            "buyToken": buy_token.address,
            "receiver": destination,
            "sellAmount": str(mantissa_sell - fee_amount),
            "buyAmount": str(buy_amount_after_fee),
            "validTo": deadline,
            "appData": web3.keccak(text="great_ape_safe").hex(),
            "feeAmount": str(fee_amount),
            "kind": "sell",
            "partiallyFillable": False,
            "sellTokenBalance": "erc20",
            "buyTokenBalance": "erc20",
            "signingScheme": "presign",
            "signature": origin,
            "from": origin,
        }
        print("ORDER PAYLOAD")
        pprint(order_payload)
        print("")

        r = requests.post(f"{self.api_url}orders", json=order_payload)
        order_uid = r.json()
        print("ORDER RESPONSE")
        pprint(order_uid)
        print("")
        assert r.ok and r.status_code == 201

        # dump order to json and add staging label if necessary
        path = "logs/trading/prod/" if self.prod else "logs/trading/staging/"
        os.makedirs(path, exist_ok=True)
        with open(f"{path}{order_uid}.json", "w+") as f:
            f.write(json.dumps(order_payload))

        if origin != self.safe.address:
            # can only sign if origin is safe
            return order_payload, order_uid

        # pre-approve the order on-chain, as set by `signingScheme`: presign
        # (otherwise signature would go in api order payload)
        # https://docs.cow.fi/smart-contracts/settlement-contract/signature-schemes
        self.settlement.setPreSignature(order_uid, True)

    def allow_relayer(self, asset, mantissa):
        """
        make sure vault relayer is approved to transferFrom the asset and
        the amount to be sold
        """
        allowance = asset.allowance(self.safe, self.vault_relayer)
        if allowance < mantissa:
            asset.approve(self.vault_relayer, mantissa)
            assert asset.allowance(self.safe, self.vault_relayer) >= mantissa
            # currently not enforced by cowswap anymore
            # print('approval needs to be executed on-chain before order can be posted to api!\n')
            # self.safe.post_safe_tx()
            # sys.exit()

    def market_sell(
        self,
        asset_sell,
        asset_buy,
        mantissa_sell,
        deadline=60 * 60,
        chunks=1,
        coef=1,
        destination=None,
    ):
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
                coef=coef,
                destination=destination,
                origin=self.safe.address,
            )

    def limit_sell(
        self,
        asset_sell,
        asset_buy,
        mantissa_sell,
        mantissa_buy,
        deadline=60 * 60,
        chunks=1,
        destination=None,
    ):
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
                deadline=deadline + n,
                coef=1,
                destination=destination,
                origin=self.safe.address,
            )

    def cancel_order(self, order_uid):
        self.settlement.invalidateOrder(order_uid)
