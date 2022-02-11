import numpy as np
from helpers.addresses import registry
from brownie import interface


class Curve:
    def __init__(self, safe):
        self.safe = safe
        # tokens
        self.crv = safe.contract(registry.eth.treasury_tokens.CRV)
        # contracts
        self.provider = safe.contract(registry.eth.curve.provider)
        self.registry = safe.contract(self.provider.get_registry())
        self.generalised_rates_info = safe.contract(self.provider.get_address(2))
        self.metapool_registry = safe.contract(self.provider.get_address(3))
        # parameters
        self.max_slippage_and_fees = 0.02
        self.is_v2 = False

    def _get_coins(self, lp_token):
        # get coin addresses from registry for a specific `lp_token`
        pool = self._get_pool_from_lp_token(lp_token)
        true_length = self.registry.get_n_coins(pool)[0]
        return [pool.coins(i) for i in range(true_length)]

    def _get_registry(self, lp_token):
        # get corresponding registry of lp token, either metapool or `normal`
        if self.is_v2:
            return self.registry
        try:
            if "Factory" in lp_token.name():
                return self.metapool_registry
            else:
                return self.registry
        except:
            return self.registry

    def _get_pool_from_lp_token(self, lp_token):
        if self.is_v2:
            try:
                pool_addr = interface.ICurveLP(lp_token).minter()
                return interface.ICurvePoolV2(pool_addr, owner=self.safe.account)
            except:
                # pool/token are the same
                return interface.ICurvePoolV2(lp_token, owner=self.safe.account)
        else:
            registry = self._get_registry(lp_token)
            if registry == self.metapool_registry:
                return interface.IStableSwap2Pool(
                    lp_token, owner=self.safe.account
                )
            else:
                pool_addr = self.registry.get_pool_from_lp_token(lp_token)
                return interface.ICurvePool(pool_addr, owner=self.safe.account)
   
 
    def _get_coin_indices(self, lp_token, pool, asset_in, asset_out):
        if self.is_v2:
            coins = self._get_coins(lp_token)
            i = None
            j = None
            for coin in coins:
                if coin == asset_in:
                    i = coins.index(coin)
                if coin == asset_out:
                    j = coins.index(coin)
            assert i != None and j != None
        else:
            registry = self._get_registry(lp_token)
            i, j, _ = registry.get_coin_indices(
                pool, asset_in, asset_out
            )
        return i, j


    def _get_n_coins(self, lp_token):
        registry = self._get_registry(lp_token)
        pool = self._get_pool_from_lp_token(lp_token)
        if not self.is_v2 and registry == self.metapool_registry:
            return registry.get_n_coins(pool)
        else:
            return registry.get_n_coins(pool)[0] # note [1] tells us if there is a wrapped coin!

    def _get_coin_indices(self, lp_token, pool, asset_in, asset_out):
        if self.is_v2:
            coins = self._get_coins(lp_token)
            i = None
            j = None
            for coin in coins:
                if coin == asset_in:
                    i = coins.index(coin)
                if coin == asset_out:
                    j = coins.index(coin)
            assert i != None and j != None
        else:
            registry = self._get_registry(lp_token)
            i, j, _ = registry.get_coin_indices(pool, asset_in, asset_out)
        return i, j

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
        registry = self._get_registry(lp_token)
        pool = self._get_pool_from_lp_token(lp_token)
        n_coins = self._get_n_coins(lp_token)

        if type(mantissas) is not list and asset is not None:
            mantissa = mantissas
            assert mantissa > 0
            mantissas = list(np.zeros(n_coins))
            for i, coin in enumerate(registry.get_coins(pool)):
                if coin == asset.address:
                    mantissas[i] = mantissa
                    break
            # make sure we found the right slot and populated it
            assert (np.array(mantissas) > 0).any()
        assert n_coins == len(mantissas)

        if self.is_v2:
            expected = pool.calc_token_amount(mantissas)
        else:
            expected = pool.calc_token_amount(mantissas, 1)
        # approve for assets corresponding to mantissas
        for i, mantissa in enumerate(mantissas):
            if mantissa > 0:
                asset = pool.coins(i)
                interface.ERC20(asset).approve(
                    pool, mantissa, {'from': self.safe.account}
                )
        bal_before = lp_token.balanceOf(self.safe)
        pool.add_liquidity(
            mantissas, expected * (1 - self.max_slippage_and_fees)
        )
        assert lp_token.balanceOf(self.safe) > bal_before

    def withdraw(self, lp_token, mantissa):
        # unwrap `mantissa` amount of lp_token back to its underlyings
        # (in same ratio as pool is currently in)
        # https://curve.readthedocs.io/exchange-pools.html#StableSwap.remove_liquidity
        pool = self._get_pool_from_lp_token(lp_token)

        n_coins = self._get_n_coins(lp_token)
        # TODO: slippage and stuff
        minima = list(np.zeros(n_coins))

        receivables = pool.remove_liquidity(mantissa, minima).return_value
        # some pools (eg 3pool) do not return `receivables` as per the standard api
        if receivables is not None:
            assert (np.array(receivables) > 0).all()

    def withdraw_to_one_coin(self, lp_token, mantissa, asset):
        # unwrap `mantissa` amount of `lp_token` but single sided; into `asset`
        # https://curve.readthedocs.io/exchange-pools.html#StableSwap.remove_liquidity_one_coin
        pool = self._get_pool_from_lp_token(lp_token)
        for i, coin in enumerate(self.registry.get_coins(pool)):
            if coin == asset.address:
                expected = pool.calc_withdraw_one_coin(mantissa, i)
                receiveable = pool.remove_liquidity_one_coin(
                    mantissa, i, expected * (1 - self.max_slippage_and_fees)
                ).return_value
                # some pools (eg 3pool) do not return `receivables` as per the standard api
                if receiveable is not None:
                    assert receiveable > 0
                return
        # could not find `asset` in `lp_token`
        raise

    def withdraw_to_one_coin_zapper(self, zapper, base_pool, pool, mantissa, asset):
        # approve zapper to allow `transferFrom`
        pool.approve(zapper, mantissa)

        zap = interface.ICurveZap(zapper, owner=self.safe.account)
        # note: tried to acess BASE_POOL constant val, but unable..., added another argument
        for i, coin in enumerate(self.registry.get_coins(base_pool)):
            if coin == asset.address:
                # summing one unit into `i` cause the deduction here of `MAX_COIN`
                # https://etherscan.io/address/0x7abdbaf29929e7f8621b757d2a7c04d78d633834#code#L194
                expected = zap.calc_withdraw_one_coin(pool, mantissa, i + 1)
                receiveable = zap.remove_liquidity_one_coin(
                    pool, mantissa, i + 1, expected * (1 - self.max_slippage_and_fees)
                ).return_value
                if receiveable is not None:
                    assert receiveable > 0
                return
        raise
        
    def swap(self, lp_token, asset_in, asset_out, mantissa):
        # swap `asset_in` (amount: `mantissa`) for `asset_out`
        # https://curve.readthedocs.io/factory-pools.html?highlight=exchange#StableSwap.exchange
        # https://curve.readthedocs.io/registry-exchanges.html?highlight=get_best_rate#finding-pools-and-swap-rates
        pool = self._get_pool_from_lp_token(lp_token)
        self._swap(lp_token, pool, asset_in, asset_out, mantissa)

    def _swap(self, lp_token, pool, asset_in, asset_out, mantissa):
        # helper for common functionalities despite of the registry/pool route
        initial_asset_out_balance = asset_out.balanceOf(self.safe)
        asset_in.approve(pool, mantissa)
        i, j = self._get_coin_indices(lp_token, pool, asset_in, asset_out)
        expected = pool.get_dy(i, j, mantissa) * (1 - self.max_slippage_and_fees)
        # L139 docs ref
        pool.exchange(i, j, mantissa, expected)
        assert asset_out.balanceOf(self.safe) >= initial_asset_out_balance + expected