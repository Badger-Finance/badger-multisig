from collections import namedtuple
import math

from brownie import chain, interface, ZERO_ADDRESS
from rich.prompt import Confirm

from great_ape_safe.ape_api.uni_v3 import UniV3
from helpers.addresses import r


# https://etherscan.io/address/0xb5087F95643A9a4069471A28d32C569D9bd57fE4#code#L1415
BunniKey = namedtuple("BunniKey", ["pool", "tickLower", "tickUpper"])

# https://etherscan.io/address/0xb5087F95643A9a4069471A28d32C569D9bd57fE4#code#L1874
DepositParams = namedtuple(
    "DepositParams",
    [
        "key",
        "amount0Desired",
        "amount1Desired",
        "amount0Min",
        "amount1Min",
        "deadline",
        "recipient",
    ],
)

# https://etherscan.io/address/0xb5087F95643A9a4069471A28d32C569D9bd57fE4#code#L1913
WithdrawParams = namedtuple(
    "WithdrawParams",
    ["key", "recipient", "shares", "amount0Min", "amount1Min", "deadline"],
)


class Bunni(UniV3):
    def __init__(
        self, safe, bunni_token_addr=None, pool_addr=None, range0=None, range1=None
    ):
        super().__init__(safe)
        self.safe = safe
        self.hub = safe.contract(r.bunni.hub)
        self.gauge_factory = safe.contract(r.bunni.gauge_factory)
        self.minter = safe.contract(r.bunni.minter)
        self.lit = interface.ERC20(r.bunni.LIT, owner=self.safe.account)
        self.olit = interface.IOptionsToken(r.bunni.oLIT, owner=self.safe.account)
        self.olit_oracle = interface.IBalancerOracle(r.bunni.oLIT_oracle)
        self.lens = interface.IBunniLens(r.bunni.lens)

        self.set_bunni_key(bunni_token_addr, pool_addr, range0, range1)

        self.slippage = 0.97
        self.deadline = 60 * 60 * 12
        self.olit_discount_pct_threshold = 50

    def set_bunni_key(
        self, bunni_token_addr=None, pool_addr=None, range0=None, range1=None
    ):
        # must provide either a bunni token address or a pool address and range
        if bunni_token_addr:
            self.bunni_key = self.bunni_key_from_token(bunni_token_addr)
        else:
            self.bunni_key = BunniKey(
                pool_addr, *self.ranges_to_ticks(pool_addr, range0, range1)
            )

    def bunni_key_from_token(self, token_addr):
        bunni_token = interface.IBunniToken(token_addr)
        return BunniKey(
            bunni_token.pool(), bunni_token.tickLower(), bunni_token.tickUpper()
        )

    def ranges_to_ticks(self, pool_addr, range0, range1):
        # ranges should be in terms of token0/token1
        pool = interface.IUniswapV3Pool(pool_addr)
        token0 = self.safe.contract(pool.token0())
        token1 = self.safe.contract(pool.token1())

        decimals_diff = token1.decimals() - token0.decimals()
        lower_tick = int(
            math.log((1 / range1) * 10 ** decimals_diff, 1.0001) // 60 * 60
        )
        upper_tick = int(
            math.log((1 / range0) * 10 ** decimals_diff, 1.0001) // 60 * 60
        )
        return lower_tick, upper_tick

    def deposit(self, amount0, amount1, destination=None):
        """
        deposit `amount0` and `amount1` of token0 and token1 into its
        bunni token
        """
        destination = destination or self.safe.address
        pool = interface.IUniswapV3Pool(self.bunni_key.pool)
        token0 = self.safe.contract(pool.token0())
        token1 = self.safe.contract(pool.token1())

        bunni_token_addr = self.hub.getBunniToken(self.bunni_key)

        if bunni_token_addr == ZERO_ADDRESS:
            bunni_token_addr = self.deploy_bunni_token()

        bunni_token = interface.IBunniToken(bunni_token_addr)

        token0_min, token1_min = self.calc_min_amounts(
            pool, amount0, amount1, self.bunni_key.tickLower, self.bunni_key.tickUpper
        )

        deposit_params = DepositParams(
            self.bunni_key,
            amount0,
            amount1,
            token0_min * self.slippage,
            token1_min * self.slippage,
            chain.time() + self.deadline,
            destination,
        )

        if amount0 > 0:
            token0.approve(self.hub, amount0), token0.approve(self.router, amount0)
        if amount1 > 0:
            token1.approve(self.hub, amount1), token1.approve(self.router, amount1)

        bal_before = bunni_token.balanceOf(destination)

        # https://etherscan.io/address/0xb5087F95643A9a4069471A28d32C569D9bd57fE4#code#L1897
        self.hub.deposit(deposit_params)

        assert bunni_token.balanceOf(destination) > bal_before
        return bunni_token_addr

    def withdraw(self, shares=None, destination=None):
        """
        withdraw `shares` of bunni_tokens and receive the underlying
        token0 and token1
        """
        destination = destination or self.safe.address
        bunni_token_addr = self.hub.getBunniToken(self.bunni_key)
        assert bunni_token_addr != ZERO_ADDRESS

        shares = shares or interface.IBunniToken(bunni_token_addr).balanceOf(
            destination
        )

        ppfs_token0, ppfs_token1 = self.lens.pricePerFullShare(self.bunni_key)[1:]
        min_amount0 = (shares * ppfs_token0 / 1e18) * self.slippage
        min_amount1 = (shares * ppfs_token1 / 1e18) * self.slippage

        # TODO: calc min amounts
        withdraw_params = WithdrawParams(
            self.bunni_key,
            destination,
            shares,
            min_amount0,
            min_amount1,
            chain.time() + self.deadline,
        )

        # https://etherscan.io/address/0xb5087F95643A9a4069471A28d32C569D9bd57fE4#code#L2409
        amount0, amount1 = self.hub.withdraw(withdraw_params).return_value[1:]

        assert amount0 > 0 and amount1 > 0

    def deploy_bunni_token(self):
        return self.hub.deployBunniToken(self.bunni_key).return_value

    def deploy_gauge(self, relative_weight_cap):
        # https://etherscan.io/address/0x822e5828cb9c0e2ad2dc5035577e6d63b672d0e2#code#L1284
        return self.gauge_factory.create(
            self.bunni_key, relative_weight_cap
        ).return_value

    def stake(self, gauge_addr, mantissa=None, claim=True, destination=None):
        """
        stake `mantissa` amount of bunni token into its corresponding
        `gauge_addr`
        """
        destination = destination or self.safe.address
        gauge = self.safe.contract(gauge_addr)
        bunni_token = interface.IBunniToken(gauge.lp_token(), owner=self.safe.account)

        assert bunni_token == self.hub.getBunniToken(
            self.bunni_key
        ), f"bunni token mismatch, {bunni_token} != {self.hub.getBunniToken(self.bunni_key)}"

        mantissa = mantissa or bunni_token.balanceOf(self.safe)
        gauge_before = gauge.balanceOf(destination)

        bunni_token.approve(gauge, mantissa)
        gauge.deposit(mantissa, destination, claim)

        assert gauge.balanceOf(destination) == mantissa + gauge_before

    def unstake(self, gauge_addr, mantissa=None, claim=True):
        """
        unstake `mantissa` shares from `gauge_addr` and receive the
        corresponding bunni token
        """
        gauge = self.safe.contract(gauge_addr)
        bunni_token = interface.IBunniToken(gauge.lp_token(), owner=self.safe.account)

        bunni_before = bunni_token.balanceOf(self.safe)
        mantissa = mantissa or gauge.balanceOf(self.safe)

        gauge.withdraw(mantissa, claim)

        assert bunni_token.balanceOf(self.safe) == bunni_before + mantissa

    def claim_rewards(self, gauge_addr):
        """
        claim oLIT rewards from `gauge_addr`
        """
        discount_pct = self.olit_oracle.multiplier() / 100
        if discount_pct < self.olit_discount_pct_threshold:
            assert Confirm.ask(f"WARNING: oLIT discount is: {discount_pct}%. Proceed?")
        before_olit = self.olit.balanceOf(self.safe)

        # https://etherscan.io/address/0xF087521Ffca0Fa8A43F5C445773aB37C5f574DA0#code#L452
        self.minter.mint(gauge_addr)

        assert self.olit.balanceOf(self.safe) > before_olit

    def exercise_olit(self, mantissa=None):
        """
        exercise oLIT option and receive LIT
        """
        payment_token = self.safe.contract(self.olit.paymentToken())
        mantissa = mantissa or self.olit.balanceOf(self.safe)

        price = self.olit_oracle.getPrice()
        expected_payment_amount = math.ceil(
            (self.olit.balanceOf(self.safe) * price) / 1e18
        )

        assert payment_token.balanceOf(self.safe) >= expected_payment_amount

        olit_before = self.olit.balanceOf(self.safe)
        lit_before = self.lit.balanceOf(self.safe)
        weth_before = payment_token.balanceOf(self.safe)

        payment_token.approve(self.olit, expected_payment_amount)

        # https://etherscan.io/address/0x627fee87d0D9D2c55098A06ac805Db8F98B158Aa#code#F5#L140
        self.olit.exercise(mantissa, expected_payment_amount, self.safe)

        assert self.olit.balanceOf(self.safe) == olit_before - mantissa
        assert self.lit.balanceOf(self.safe) == lit_before + mantissa
        assert (
            payment_token.balanceOf(self.safe) == weth_before - expected_payment_amount
        )

    def compound(self):
        """
        compounds all fees back into the uniswap pool
        """
        # https://etherscan.io/address/0xb5087F95643A9a4069471A28d32C569D9bd57fE4#code#L2481
        added_liq = self.hub.compound(self.bunni_key).return_value[0]

        assert added_liq > 0
