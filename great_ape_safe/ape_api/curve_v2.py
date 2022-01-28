import numpy as np
from helpers.addresses import registry
from brownie import interface


class Curve_v2():
    def __init__(self, safe):
        self.safe       = safe
        # tokens
        self.crv        = safe.contract(registry.eth.treasury_tokens.CRV)
        # contracts
        self.provider   = safe.contract(registry.eth.curve.provider)
        self.registry   = safe.contract(self.provider.get_registry())
        # parameters
        self.max_slippage_and_fees = .02


    def deposit(self, lp_token, pool_addr, mantissas, asset=None):
        # wrap `mantissas` of underlying tokens into a curve `lp_token`
        # `mantissas` do not need to be balanced in any way
        # if `mantissas` is not a list but an int, `asset` needs to be specified
        # as well, in order to automatically determine correct slot number
        # https://curve.readthedocs.io/exchange-pools.html#StableSwap.add_liquidity
        #
        # TODO: find and route through zaps automatically
        # TODO: could pass dict to mantissas with {address: mantissa} and sort
        #       out proper ordering automatically?
        pool = interface.ICurveFi(pool_addr)
        if type(mantissas) is int and asset is not None:
            mantissa = mantissas
            assert mantissa > 0
            pool_addr = self.registry.get_pool_from_lp_token(lp_token)
            n_coins = self.registry.get_n_coins(pool_addr)[0]
            mantissas = list(np.zeros(n_coins))
            for i, coin in enumerate(self.registry.get_coins(pool_addr)):
                if coin == asset.address:
                    mantissas[i] = mantissa
                    break
        expected = pool.calc_token_amount(mantissas)
        # approve for assets corresponding to mantissas
        for i, mantissa in enumerate(mantissas):
            if mantissa > 0:
                asset = pool.coins(i)
                self.safe.contract(asset).approve(pool, mantissa)
        bal_before = lp_token.balanceOf(self.safe)
        pool.add_liquidity(
            mantissas,
            expected * (1 - self.max_slippage_and_fees),
            {'from': self.safe.address}
        )
        assert lp_token.balanceOf(self.safe) > bal_before
