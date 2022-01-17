import numpy as np


class Curve():
    def __init__(self, safe):
        self.safe       = safe
        # tokens
        self.crv        = safe.contract('0xD533a949740bb3306d119CC777fa900bA034cd52')
        # contracts
        self.provider   = safe.contract('0x0000000022D53366457F9d5E68Ec105046FC4383')
        self.registry   = safe.contract(self.provider.get_registry())
        # parameters
        self.max_slippage_and_fees = .02


    def _get_coins(self, lp_token):
        # get coin addresses from registry for a specific `lp_token`
        pool_addr = self.registry.get_pool_from_lp_token(lp_token)
        true_length = self.registry.get_n_coins(pool_addr)[0]
        return list(self.registry.get_coins(pool_addr))[:true_length]


    def deposit(self, lp_token, mantissas, asset=None):
        # wrap `mantissas` of underlying tokens into a curve `lp_token`
        # `mantissas` do not need to be balanced in any way
        # if `mantissas` is not a list but an int, `asset` needs to be specified
        # as well, in order to automatically determine correct slot number
        # https://curve.readthedocs.io/exchange-pools.html#StableSwap.add_liquidity
        #
        # TODO: find and route through zaps automatically
        # TODO: could pass dict to mantissas with {address: mantissa} and sort
        #       out proper ordering automatically?
        pool_addr = self.registry.get_pool_from_lp_token(lp_token)
        pool = self.safe.contract(pool_addr)
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
            # make sure we found the right slot and populated it
            assert (np.array(mantissas) > 0).any()
        assert self.registry.get_n_coins(pool_addr)[0] == len(mantissas)
        expected = pool.calc_token_amount(mantissas, 1)
        # approve for assets corresponding to mantissas
        for i, mantissa in enumerate(mantissas):
            if mantissa > 0:
                asset = self.registry.get_coins(pool_addr)[i]
                self.safe.contract(asset).approve(pool, mantissa)
        bal_before = lp_token.balanceOf(self.safe)
        pool.add_liquidity(
            mantissas,
            expected * (1 - self.max_slippage_and_fees)
        )
        assert lp_token.balanceOf(self.safe) > bal_before


    def withdraw(self, lp_token, mantissa):
        # unwrap `mantissa` amount of lp_token back to its underlyings
        # (in same ratio as pool is currently in)
        # https://curve.readthedocs.io/exchange-pools.html#StableSwap.remove_liquidity
        pool_addr = self.registry.get_pool_from_lp_token(lp_token)
        n_coins = self.registry.get_n_coins(pool_addr)[0] # note [1] tells us if there is a wrapped coin!
        # TODO: slippage and stuff

        minima = list(np.zeros(n_coins))
        receivables = self.safe.contract(pool_addr).remove_liquidity(mantissa, minima).return_value
        # some pools (eg 3pool) do not return `receivables` as per the standard api
        if receivables is not None:
            assert (np.array(receivables) > 0).all()


    def withdraw_to_one_coin(self, lp_token, mantissa, asset):
        # unwrap `mantissa` amount of `lp_token` but single sided; into `asset`
        # https://curve.readthedocs.io/exchange-pools.html#StableSwap.remove_liquidity_one_coin
        pool_addr = self.registry.get_pool_from_lp_token(lp_token)
        pool = self.safe.contract(pool_addr)
        for i, coin in enumerate(self.registry.get_coins(pool_addr)):
            if coin == asset.address:
                expected = pool.calc_withdraw_one_coin(mantissa, i)
                receiveable = pool.remove_liquidity_one_coin(
                    mantissa,
                    i,
                    expected * (1 - self.max_slippage_and_fees)
                ).return_value
                # some pools (eg 3pool) do not return `receivables` as per the standard api
                if receiveable is not None:
                    assert receiveable > 0
                return
        # could not find `asset` in `lp_token`
        raise
