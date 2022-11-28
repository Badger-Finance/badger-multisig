import numpy as np
from helpers.addresses import registry
from brownie import Contract, ZERO_ADDRESS, interface
from brownie.exceptions import VirtualMachineError


class Curve:
    def __init__(self, safe):
        self.safe = safe
        # tokens
        self.crv = interface.ERC20(registry.eth.treasury_tokens.CRV)
        # contracts
        self.provider = safe.contract(registry.eth.curve.provider)
        self.registry = safe.contract(self.provider.get_registry())
        self.pool_info = safe.contract(self.provider.get_address(1))
        self.exchanger = safe.contract(self.provider.get_address(2))
        self.factory_registry = safe.contract(self.provider.get_address(3))
        self.crypto_registry = safe.contract(self.provider.get_address(5))
        # parameters
        self.max_slippage_and_fees = 0.02
        self.is_v2 = False

    def _get_coins(self, lp_token):
        # get coin addresses from registry for a specific `lp_token`
        pool = self._get_pool_from_lp_token(lp_token)
        true_length = self.registry.get_n_coins(pool)[0]
        return [pool.coins(i) for i in range(true_length)]

    def _get_registry(self, pool):
        # get corresponding registry of lp token, either the 'normal' one,
        # metapool, crypto or v2 (factory-crypto).
        if self.is_v2:
            return self.factory_crypto_registry
        cryptos = []
        for i in range(32):
            addr = self.crypto_registry.pool_list(i)
            if addr is ZERO_ADDRESS:
                break
            cryptos.append(addr)
        if pool in cryptos:
            return self.crypto_registry
        try:
            if "Factory" in pool.name():
                return self.factory_registry
            else:
                return self.registry
        except:
            return self.registry

    def _get_pool_from_lp_token(self, lp_token):
        pool_addr = None
        is_normal = self.registry.get_pool_from_lp_token(lp_token)
        if is_normal != ZERO_ADDRESS:
            pool_addr = is_normal
        is_factory = self.factory_registry.get_coins(lp_token)[0]
        if is_factory != ZERO_ADDRESS:
            pool_addr = lp_token.address
        if pool_addr is None:
            # is crypto or factory-crypto
            pool_addr = lp_token.minter()
        return Contract(pool_addr, owner=self.safe.account)

    def _get_coin_indices(self, pool, asset_in, asset_out):
        if self.is_v2:
            coins = self._get_coins(pool)
            i = None
            j = None
            for coin in coins:
                if coin == asset_in:
                    i = coins.index(coin)
                if coin == asset_out:
                    j = coins.index(coin)
            assert i != None and j != None
        else:
            registry = self._get_registry(pool)
            # workaround; crypo_registry only returns 2 vars, whereas old style
            # returned 3
            indices = registry.get_coin_indices(pool, asset_in, asset_out)
            i = indices[0]
            j = indices[1]
        return i, j

    def _get_n_coins(self, lp_token):
        pool = self._get_pool_from_lp_token(lp_token)
        if self.is_v2:
            return self.factory_crypto_registry.get_n_coins(pool)[0]
        on_normal_registry = self.registry.get_n_coins(pool)
        if on_normal_registry != (0, 0):
            return on_normal_registry[0]
        else:
            registry = self._get_registry(pool)
            return registry.get_n_coins(pool)

    def _pool_has_wrapped_coins(self, pool):
        registry = self._get_registry(pool)
        if registry == self.crypto_registry:
            return False
        try:
            registry.get_underlying_balances(pool)
            return True
        except VirtualMachineError:
            return False

    def _pool_supports_underlying(self, pool):
        return "exchange_underlying" in pool.signatures.keys()

    def deposit(self, lp_token, mantissas, asset=None, seeding=False):
        # wrap `mantissas` of underlying tokens into a curve `lp_token`
        # `mantissas` do not need to be balanced in any way
        # if `mantissas` is not a list but an int, `asset` needs to be specified
        # as well, in order to automatically determine correct slot number
        # https://curve.readthedocs.io/exchange-pools.html#StableSwap.add_liquidity
        #
        # TODO: find and route through zaps automatically
        # TODO: could pass dict to mantissas with {address: mantissa} and sort
        #       out proper ordering automatically?
        pool = self._get_pool_from_lp_token(lp_token)
        registry = self._get_registry(pool)
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

        if not seeding:
            if self.is_v2:
                expected = pool.calc_token_amount(mantissas)
            else:
                expected = pool.calc_token_amount(mantissas, 1)
        else:
            expected = 0
        # approve for assets corresponding to mantissas
        for i, mantissa in enumerate(mantissas):
            if mantissa > 0:
                asset = pool.coins(i)
                interface.ERC20(asset).approve(
                    pool, mantissa, {"from": self.safe.account}
                )
        bal_before = lp_token.balanceOf(self.safe)
        pool.add_liquidity(mantissas, expected * (1 - self.max_slippage_and_fees))
        assert lp_token.balanceOf(self.safe) > bal_before

    def deposit_zapper(self, zapper, pool, assets, mantissas, seeding=False):
        for asset, mantissa in zip(assets, mantissas):
            if mantissa > 0:
                asset.approve(zapper, mantissa)
        if not seeding:
            expected = zapper.calc_token_amount(pool, mantissas)
        else:
            expected = 0
        zapper.add_liquidity(pool, mantissas, expected)

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
        registry = self._get_registry(pool)
        for i, coin in enumerate(registry.get_coins(pool)):
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

    def swap(self, asset_in, asset_out, mantissa):
        # swap `asset_in` (amount: `mantissa`) for `asset_out`
        # https://curve.readthedocs.io/factory-pools.html?highlight=exchange#StableSwap.exchange
        # https://curve.readthedocs.io/registry-exchanges.html?highlight=get_best_rate#finding-pools-and-swap-rates
        try:
            pool_addr = self.exchanger.get_best_rate(asset_in, asset_out, mantissa)[0]
        except VirtualMachineError:
            raise Exception("no direct swap path known")
        if pool_addr == ZERO_ADDRESS:
            raise Exception("no direct swap path known")
        # TODO: sort interfaces
        pool = Contract(pool_addr, owner=self.safe.account)
        self._swap(pool, asset_in, asset_out, mantissa)

    def _swap(self, pool, asset_in, asset_out, mantissa):
        # helper for common functionalities despite of the registry/pool route
        initial_asset_out_balance = asset_out.balanceOf(self.safe)
        asset_in.approve(pool, mantissa)
        i, j = self._get_coin_indices(pool, asset_in, asset_out)
        # L139 docs ref
        if self._pool_has_wrapped_coins(pool) and self._pool_supports_underlying(pool):
            expected = pool.get_dy_underlying(i, j, mantissa) * (
                1 - self.max_slippage_and_fees
            )
            pool.exchange_underlying(i, j, mantissa, expected)
        else:
            expected = pool.get_dy(i, j, mantissa) * (1 - self.max_slippage_and_fees)
            pool.exchange(i, j, mantissa, expected)
        assert asset_out.balanceOf(self.safe) >= initial_asset_out_balance + expected
