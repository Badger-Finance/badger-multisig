from decimal import Decimal
import requests
import json

from brownie import ZERO_ADDRESS, Contract
from helpers.addresses import registry
from web3 import Web3
import eth_abi

from great_ape_safe.ape_api.helpers.balancer.stable_math import StableMath
from great_ape_safe.ape_api.helpers.balancer.weighted_math import WeightedMath
from great_ape_safe.ape_api.helpers.balancer.queries import pool_tokens_query


class Balancer():
    def __init__(self, safe):
        self.safe = safe
        # contracts
        self.vault = safe.contract(registry.eth.balancer.vault)
        self.gauge_factory = safe.contract(registry.eth.balancer.gauge_factory)
        # parameters
        self.max_slippage = Decimal(0.02)
        self.pool_query_liquidity_threshold = Decimal(10_000) # USD
        self.dusty = 0.99
        # misc
        self.subgraph = 'https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-v2'


    def get_pool_data(self, update_cache=False):
        # no on-chain registry, so pool data is cached locally
        # used for pool look up based on underlyings
        # `update_cache` to query subgraph for new pools above liquidity threshold
        if update_cache:
            res = requests.post(self.subgraph, json={'query': pool_tokens_query}).json()
            pool_data = res['data']['pools']
            pool_data_filtered = [x for x in pool_data if
                            Decimal(x['totalLiquidity']) > self.pool_query_liquidity_threshold]
            with open('great_ape_safe/ape_api/helpers/balancer/pools.json','w') as f:
                json.dump(pool_data_filtered, f)
            return pool_data_filtered

        with open('great_ape_safe/ape_api/helpers/balancer/pools.json') as f:
            data = json.load(f)
            return data


    def find_pool_for_underlyings(self, underlyings):
        # find pools with matching underlyings from cached pool data
        pool_data = self.get_pool_data()
        match = None
        for pool in pool_data:
            tokens = [Web3.toChecksumAddress(x['address']) for x in pool['tokens']]
            if underlyings == tokens:
                if match:
                    raise Exception('multiple matching pools exist, provide `pool`')
                match = pool['id']
        if not match:
            raise Exception('no pool found for underlyings')
        return match


    def order_tokens(self, underlyings, mantissas):
        # helper function to order tokens/amounts numerically
        tokens = dict(zip(underlyings, mantissas))
        sorted_tokens = dict(sorted(tokens.items()))
        return zip(*sorted_tokens.items())


    def pool_type(self, pool_id):
        pool_data = self.get_pool_data()
        for pool in pool_data:
            if pool['id'] == pool_id:
                pool_type = pool['poolType']
                weight = pool['totalWeight']
                if pool_type == 'Weighted':
                    return 'Weighted'
                elif 'Stable' in pool_type:
                    return 'Stable'
                elif weight == '0':
                    return 'Stable'
                return 'Weighted'


    def deposit_and_stake(
        self, underlyings, mantissas, pool=None, stake=True, is_eth=False, destination=None
    ):
        # given underlyings and their amounts, deposit and stake `underlyings`

        # https://dev.balancer.fi/resources/joins-and-exits/pool-joins#token-ordering
        underlyings, mantissas = \
            self.order_tokens([x.address for x in underlyings], mantissas)

        if pool:
            pool_id = pool.getPoolId()
        else:
            pool_id = self.find_pool_for_underlyings(list(underlyings))
            pool = self.safe.contract(self.vault.getPool(pool_id)[0])

        tokens, reserves, _ = self.vault.getPoolTokens(pool_id)

        if self.pool_type(pool_id) == 'Stable':
            bpt_out = StableMath.calcBptOutGivenExactTokensIn(pool, reserves, mantissas)
        else:
            bpt_out = WeightedMath.calc_bpt_out_given_exact_tokens_in(pool, reserves, mantissas)

        min_bpt_out = int(bpt_out * (1 - self.max_slippage))

        # https://dev.balancer.fi/resources/joins-and-exits/pool-joins#encoding-how-do-i-encode
        data_encoded = eth_abi.encode_abi(
            ['uint256', 'uint256[]', 'uint256'],
            [1, mantissas, min_bpt_out]
            )

        if is_eth:
            underlyings = list(underlyings)
            weth_index = underlyings.index(registry.eth.treasury_tokens.WETH)
            underlyings[weth_index] = ZERO_ADDRESS

        # https://dev.balancer.fi/resources/joins-and-exits/pool-joins#arguments-explained
        request = (
            underlyings,
            mantissas,
            data_encoded,
            False
        )

        for i, token in enumerate(tokens):
            if token != ZERO_ADDRESS:
                token = self.safe.contract(token)
                token.approve(self.vault, mantissas[i])

        self._deposit_and_stake(
            pool, request, stake=stake, destination=destination
        )


    def deposit_and_stake_single_asset(
         self, underlying, mantissa, pool, stake=True, is_eth=False, destination=None
    ):
        pool_id = pool.getPoolId()
        underlyings, reserves, _ = self.vault.getPoolTokens(pool_id)
        mantissas = [mantissa if x == underlying.address else 0 for x in underlyings]

        if self.pool_type(pool_id) == 'Stable':
            bpt_out = StableMath.calcBptOutGivenExactTokensIn(pool, reserves, mantissas)
        else:
            bpt_out = WeightedMath.calc_bpt_out_given_exact_tokens_in(pool, reserves, mantissas)

        min_bpt_out = int(bpt_out * (1 - self.max_slippage))

        data_encoded = eth_abi.encode_abi(
            ['uint256', 'uint256', 'uint256'],
            [2, min_bpt_out, underlyings.index(underlying.address)]
            )

        if is_eth:
            underlyings = list(underlyings)
            weth_index = underlyings.index(registry.eth.treasury_tokens.WETH)
            underlyings[weth_index] = ZERO_ADDRESS

        request = (
            underlyings,
            mantissas,
            data_encoded,
            False
        )

        underlying.approve(self.vault, mantissa)

        self._deposit_and_stake(
            pool, request, stake=stake, destination=destination
        )


    def _deposit_and_stake(
        self, pool, request, stake=True, destination=None
    ):
        destination = self.safe if not destination else destination
        pool_id = pool.getPoolId()

        pool_recipient = self.safe if stake else destination
        balance_before = pool.balanceOf(pool_recipient)

        # https://dev.balancer.fi/resources/joins-and-exits/pool-joins
        self.vault.joinPool(
            pool_id, self.safe, pool_recipient, request
        )

        balance_delta = pool.balanceOf(pool_recipient) - balance_before
        assert balance_delta > 0

        if stake:
            gauge_address = self.gauge_factory.getPoolGauge(pool)

            if gauge_address == ZERO_ADDRESS:
                raise Exception(f'no gauge for {pool_id}')

            gauge = self.safe.contract(gauge_address)
            balance_before = gauge.balanceOf(self.safe)
            pool.approve(gauge, balance_delta)
            gauge.deposit(balance_delta * self.dusty, destination)

            assert gauge.balanceOf(destination) > balance_before


    def unstake_all_and_withdraw_all(
        self, underlyings=None, pool=None, unstake=True, claim=True, is_eth=False, destination=None
    ):
        if not underlyings and not pool:
            raise TypeError('must provide either underlyings or pool')

        if underlyings:
            underlyings = sorted([x.address for x in underlyings])
            pool_id = self.find_pool_for_underlyings(underlyings)
            pool = self.safe.contract(self.vault.getPool(pool_id)[0])
        else:
            pool_id = pool.getPoolId()

        underlyings, reserves, _ = self.vault.getPoolTokens(pool_id)
        gauge = self.safe.contract(self.gauge_factory.getPoolGauge(pool))

        amount_in = pool.balanceOf(self.safe)

        if unstake:
            amount_in += gauge.balanceOf(self.safe)


        data_encoded = eth_abi.encode_abi(
            ['uint256', 'uint256'],
            [1, amount_in]
            )


        if self.pool_type(pool_id) == 'Stable':
            underlyings_out = StableMath.calcTokensOutGivenExactBptIn(
                pool, reserves, amount_in
            )
        else:
            underlyings_out = WeightedMath.calc_tokens_out_given_exact_bpt_in(
            pool, reserves, amount_in
        )

        min_underlyings_out = \
            [x * (1 - self.max_slippage) for x in underlyings_out]

        if is_eth:
            underlyings = list(underlyings)
            weth_index = underlyings.index(registry.eth.treasury_tokens.WETH)
            underlyings[weth_index] = ZERO_ADDRESS

        request = (
            underlyings,
            min_underlyings_out,
            data_encoded,
            is_eth
        )

        pool.approve(self.vault, amount_in)

        self._unstake_and_withdraw_all(
            pool, request, unstake, claim, destination
        )


    def unstake_and_withdraw_all_single_asset(
        self, asset, underlyings=None, pool=None, unstake=True, claim=True, is_eth=False, destination=None
    ):
        if not underlyings and not pool:
            raise TypeError('must provide either underlyings or pool')

        if underlyings:
            underlyings = sorted([x.address for x in underlyings])
            pool_id = self.find_pool_for_underlyings(underlyings)
            pool = self.safe.contract(self.vault.getPool(pool_id)[0])
        else:
            pool_id = pool.getPoolId()

        underlyings, reserves, _ = self.vault.getPoolTokens(pool_id)
        gauge = self.safe.contract(self.gauge_factory.getPoolGauge(pool))

        amount_in = pool.balanceOf(self.safe)

        if unstake:
            amount_in += gauge.balanceOf(self.safe)

        underlying_index = underlyings.index(asset.address)

        data_encoded = eth_abi.encode_abi(
            ['uint256', 'uint256', 'uint256'],
            [0, amount_in, underlying_index]
            )


        if self.pool_type(pool_id) == 'Stable':
            underlying_out = StableMath.calcTokenOutGivenExactBptIn(
                pool, reserves, underlying_index, amount_in
            )
        else:
            underlying_out = WeightedMath.calc_token_out_given_exact_bpt_in(
                pool, reserves[underlying_index], amount_in, underlying_index
            )

        min_out = underlying_out * (1 - self.max_slippage)

        if is_eth:
            underlyings = list(underlyings)
            weth_index = underlyings.index(registry.eth.treasury_tokens.WETH)
            underlyings[weth_index] = ZERO_ADDRESS

        request = (
            underlyings,
            [min_out if x == asset.address else 0 for x in underlyings],
            data_encoded,
            False
        )

        pool.approve(self.vault, amount_in)

        self._unstake_and_withdraw_all(
            pool, request, unstake, claim, destination
        )


    def _unstake_and_withdraw_all(
        self, pool, request, unstake, claim, destination
    ):
        destination = self.safe if not destination else destination
        pool_id = pool.getPoolId()

        if unstake:
            gauge = self.safe.contract(self.gauge_factory.getPoolGauge(pool))
            balance_before_gauge = gauge.balanceOf(self.safe)
            gauge.withdraw(gauge.balanceOf(self.safe), claim)
            assert pool.balanceOf(self.safe) >= balance_before_gauge

        balances_before = [Contract(x).balanceOf(destination) for x in request[0]]

        self.vault.exitPool(
            pool_id, self.safe, destination, request
        )

        balances_after = [Contract(x).balanceOf(destination) for x in request[0]]
        assert any([x > y for x, y in zip(balances_after, balances_before)])


    def claim_all(self, underlyings=None, pool=None):
        # claim reward token from pool's gauge
        if underlyings:
            underlyings = sorted([x.address for x in underlyings])
            pool_id = self.find_pool_for_underlyings(underlyings)
            pool = self.safe.contract(self.vault.getPool(pool_id)[0])

        gauge = self.safe.contract(self.gauge_factory.getPoolGauge(pool))
        reward_address = gauge.reward_tokens(0)

        if reward_address == ZERO_ADDRESS:
            raise Exception(f'no reward token for pool')

        assert gauge.claimable_tokens.call(self.safe) > 0

        reward = self.safe.contract(reward_address)
        bal_before = reward.balanceOf(self.safe)

        gauge.claim_rewards()

        assert reward.balanceOf(self.safe) > bal_before
