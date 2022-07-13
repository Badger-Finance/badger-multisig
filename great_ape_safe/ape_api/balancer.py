from decimal import Decimal
import requests
import json

from brownie import ZERO_ADDRESS, Contract, chain, interface, web3
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
        self.vebal = safe.contract(registry.eth.balancer.veBAL)
        self.wallet_checker = safe.contract(self.vebal.smart_wallet_checker())
        self.minter = safe.contract(
            registry.eth.balancer.minter, interface.IBalancerMinter
        )
        # parameters
        self.max_slippage = Decimal(0.02)
        self.pool_query_liquidity_threshold = Decimal(10_000) # USD
        self.dusty = 0.995
        self.deadline = 60 * 60 * 12
        # misc
        self.subgraph = 'https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-v2'


    def get_amount_out(self, asset_in, asset_out, amount_in, pool=None):
        # https://dev.balancer.fi/references/contracts/apis/the-vault#querybatchswap
        underlyings = self.order_tokens([asset_in.address, asset_out.address])
        if not pool:
            pool_id = self.find_pool_for_underlyings(underlyings)
            pool = self.safe.contract(self.vault.getPool(pool_id)[0])
        else:
            pool_id = pool.getPoolId()

        asset_in_index = underlyings.index(asset_in.address)
        asset_out_index = underlyings.index(asset_out.address)
        # https://github.com/balancer-labs/balancer-v2-monorepo/blob/095648c29d4ce67dd386edd8344c1eaadf812e42/pkg/vault/contracts/interfaces/IVault.sol#L498
        calc_out_given_in = 0

        swap = [(
            pool_id,
            asset_in_index,
            asset_out_index,
            amount_in,
            b''
        )]

        funds = (
            self.safe.address, # sender
            False, # fromInternalBalance
            self.safe.address, # recipient
            False # toInternalBalance
        )

        amounts = self.vault.queryBatchSwap.call(calc_out_given_in, swap, underlyings, funds)
        return abs(amounts[asset_out_index])


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


    def find_best_pool_for_swap(self, asset_in, asset_out):
        # find pools that contain swap assets and return the one with most liq
        pool_data = self.get_pool_data()
        valid_pools = {}
        for pool in pool_data:
            tokens = [Web3.toChecksumAddress(x['address']) for x in pool['tokens']]
            if asset_in in tokens and asset_out in tokens:
                valid_pools[pool['id']] = pool['totalLiquidity']
        if len(valid_pools) > 0:
            return max(valid_pools, key=valid_pools.get)
        raise Exception('no pool found for swap')


    def order_tokens(self, underlyings, mantissas=None):
        # helper function to order tokens/amounts numerically
        if mantissas:
            tokens = dict(zip([x.lower() for x in underlyings], mantissas))
            sorted_tokens = dict(sorted(tokens.items()))
            sorted_underlyings, sorted_mantissas = zip(*sorted_tokens.items())
            underlyings_checksummed = [Web3.toChecksumAddress(x) for x in sorted_underlyings]
            return underlyings_checksummed, sorted_mantissas
        else:
            sorted_tokens = sorted([x.lower() for x in underlyings])
            return [Web3.toChecksumAddress(x) for x in sorted_tokens]


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
        raise Exception('pool not found')


    def deposit_and_stake(
        self, underlyings, mantissas, pool=None, stake=True, is_eth=False, destination=None, pool_type=None
    ):
        # given underlyings and their amounts, deposit and stake `underlyings`

        # https://dev.balancer.fi/resources/joins-and-exits/pool-joins#token-ordering
        underlyings, mantissas = \
            self.order_tokens([x.address for x in underlyings], mantissas=mantissas)

        if pool:
            pool_id = pool.getPoolId()
        else:
            pool_id = self.find_pool_for_underlyings(list(underlyings))
            pool = self.safe.contract(self.vault.getPool(pool_id)[0])

        tokens, reserves, _ = self.vault.getPoolTokens(pool_id)

        pool_type = pool_type if pool_type else self.pool_type(pool_id)

        if pool_type == 'Stable':
            # wip
            # bpt_out = StableMath.calcBptOutGivenExactTokensIn(pool, reserves, mantissas)
            bpt_out = 1
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
            # wip
            # bpt_out = StableMath.calcBptOutGivenExactTokensIn(pool, reserves, mantissas)
            bpt_out = 1
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
            self.stake_all(pool, destination, dusty=True)


    def stake(self, pool, mantissa, destination=None, dusty=False):
        pool_id = pool.getPoolId()
        destination = self.safe if not destination else destination
        gauge_address = self.gauge_factory.getPoolGauge(pool)

        if gauge_address == ZERO_ADDRESS:
            raise Exception(f'no gauge for {pool_id}')

        gauge = self.safe.contract(gauge_address)
        gauge_balance_before = gauge.balanceOf(destination)
        pool.approve(gauge, mantissa)
        if dusty:
            gauge.deposit(mantissa * self.dusty, destination)
        else:
            gauge.deposit(mantissa, destination)
        assert gauge.balanceOf(destination) > gauge_balance_before


    def stake_all(self, pool, destination=None, dusty=False):
        destination = self.safe if not destination else destination
        mantissa = pool.balanceOf(destination)
        self.stake(pool, mantissa, destination, dusty)


    def unstake(self, pool, mantissa, claim=True):
        gauge = self.safe.contract(self.gauge_factory.getPoolGauge(pool))
        bal_pool_before = pool.balanceOf(self.safe)
        gauge.withdraw(mantissa, claim)
        assert pool.balanceOf(self.safe) == bal_pool_before + mantissa


    def unstake_all(self, pool, claim=True):
        gauge = self.safe.contract(self.gauge_factory.getPoolGauge(pool))
        bal_pool_before = pool.balanceOf(self.safe)
        gauge_bal = gauge.balanceOf(self.safe)
        gauge.withdraw(gauge_bal, claim)
        assert pool.balanceOf(self.safe) == bal_pool_before + gauge_bal


    def unstake_all_and_withdraw_all(
        self, underlyings=None, pool=None, unstake=True, claim=True, is_eth=False, destination=None, pool_type=None
    ):
        if not underlyings and not pool:
            raise TypeError('must provide either underlyings or pool')

        if underlyings:
            underlyings = self.order_tokens([x.address for x in underlyings])
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

        pool_type = pool_type if pool_type else self.pool_type(pool_id)
        if pool_type == 'Stable':
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

        self._unstake_and_withdraw_all(
            pool, request, unstake, claim, destination
        )


    def unstake_and_withdraw_all_single_asset(
        self, asset, underlyings=None, pool=None, unstake=True, claim=True, is_eth=False, destination=None
    ):
        if not underlyings and not pool:
            raise TypeError('must provide either underlyings or pool')

        if underlyings:
            underlyings = self.order_tokens([x.address for x in underlyings])
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

        self._unstake_and_withdraw_all(
            pool, request, unstake, claim, destination
        )


    def _unstake_and_withdraw_all(
        self, pool, request, unstake, claim, destination
    ):
        destination = self.safe if not destination else destination
        pool_id = pool.getPoolId()

        if unstake:
            self.unstake_all(pool)

        balances_before = [Contract(x).balanceOf(destination) for x in request[0]]

        self.vault.exitPool(
            pool_id, self.safe, destination, request
        )

        balances_after = [Contract(x).balanceOf(destination) for x in request[0]]

        if request[1].count(0) == 0:
            assert all([x > y for x, y in zip(balances_after, balances_before)])
        else:
            assert any([x > y for x, y in zip(balances_after, balances_before)])


    def claim(self, underlyings=None, pool=None):
        # claim reward token from pool's gauge given `underlyings` or `pool`
        if underlyings:
            underlyings = self.order_tokens([x.address for x in underlyings])
            pool_id = self.find_pool_for_underlyings(underlyings)
            pool = self.safe.contract(self.vault.getPool(pool_id)[0])
        gauge = self.safe.contract(self.gauge_factory.getPoolGauge(pool))
        self.minter.mint(gauge)


    def claim_all(self, underlyings=None, pool=None):
        # claim reward token from pool's gauge given `underlyings` or `pool`
        if underlyings:
            underlyings = self.order_tokens([x.address for x in underlyings])
            pool_id = self.find_pool_for_underlyings(underlyings)
            pool = self.safe.contract(self.vault.getPool(pool_id)[0])

        gauge = self.safe.contract(self.gauge_factory.getPoolGauge(pool))
        reward_count = gauge.reward_count()
        assert reward_count > 0
        assert gauge.claimable_tokens.call(self.safe) > 0

        balances_before = \
            [Contract(gauge.reward_tokens(x)).balanceOf(self.safe) for x in range(reward_count)]

        gauge.claim_rewards()

        balances_after = \
            [Contract(gauge.reward_tokens(x)).balanceOf(self.safe) for x in range(reward_count)]

        assert all([x > y for x, y in zip(balances_after, balances_before)])


    def swap(self, asset_in, asset_out, mantissa_in, pool=None, destination=None):
        destination = self.safe if not destination else destination
        if pool:
            pool_id = pool.getPoolId()
        else:
            pool_id = self.find_best_pool_for_swap(asset_in.address, asset_out.address)
            pool = self.safe.contract(self.vault.getPool(pool_id)[0])

        swap_kind = 0 # 0 = GIVEN_IN, 1 = GIVEN_OUT
        user_data_encoded = eth_abi.encode_abi(['uint256'], [0])
        min_out = self.get_amount_out(asset_in, asset_out, mantissa_in, pool=pool) * (1 - self.max_slippage)

        swap_settings = (
            pool_id,
            swap_kind,
            asset_in.address,
            asset_out.address,
            mantissa_in,
            user_data_encoded
        )

        fund_settings = (
            self.safe.address, # sender
            False, # fromInternalBalance
            destination.address, # recipient
            False, # toInternalBalance
        )

        asset_in.approve(self.vault, mantissa_in)
        before_balance_out = asset_out.balanceOf(destination)

        self.vault.swap(
            swap_settings,
            fund_settings,
            min_out,
            web3.eth.getBlock(web3.eth.blockNumber).timestamp + self.deadline
        )

        assert asset_out.balanceOf(destination) >= before_balance_out + min_out


    def lock_bal(self, mantissa_bal=None, mantissa_weth=None, mantisssa_bpt=None, lock_days=365):
        '''
        if given `mantisssa_bpt` just lock bpt
        if given only `mantissa_bal` swap 20% for weth, deposit and lock
        if given only `mantissa_bal` and `mantissa_weth`, deposit and lock
        '''
        if not self.wallet_checker.check(self.safe):
            raise Exception('Safe is not whitelisted')

        if lock_days < 7:
            raise Exception('min lock_days is 7')

        bpt = self.safe.contract(self.vebal.token())
        weth = self.safe.contract(registry.eth.treasury_tokens.WETH)
        bal = self.safe.contract(registry.eth.treasury_tokens.BAL)

        swapping = not mantisssa_bpt and not mantissa_weth
        before_bal = bal.balanceOf(self.safe)
        before_weth = weth.balanceOf(self.safe) if swapping else 0

        if swapping:
            swap_mantissa = int(mantissa_bal / 5)
            self.swap(bal, weth, swap_mantissa)

        after_bal = before_bal - swap_mantissa if swapping else before_bal
        after_weth = weth.balanceOf(self.safe) - before_weth

        depositing = not mantisssa_bpt
        before_bpt = bpt.balanceOf(self.safe)

        if depositing:
            underlyings = [bal, weth]
            amounts = [int(after_bal * self.dusty), int(after_weth * self.dusty)]
            self.deposit_and_stake(underlyings, amounts, pool=bpt, stake=False)

        day = 86400
        week = day * 7
        unlock_time = ((chain.time() + day * lock_days) // week) * week

        after_bpt = ((bpt.balanceOf(self.safe) - before_bpt) * self.dusty
                        if depositing else mantisssa_bpt)

        bpt.approve(self.vebal, after_bpt)

        self.vebal.create_lock(after_bpt, unlock_time)

        assert bpt.balanceOf(self.safe) < after_bpt
