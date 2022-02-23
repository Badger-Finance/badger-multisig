from brownie import interface, web3
from helpers.addresses import registry
from sympy import Symbol
from sympy.solvers import solve

class UniV2:
    def __init__(self, safe):
        self.safe = safe

        self.router = safe.contract(registry.eth.uniswap.routerV2)
        self.factory = safe.contract(registry.eth.uniswap.factoryV2)

        self.max_slippage = 0.02
        self.max_weth_unwrap = 0.01
        self.deadline = 60 * 60 * 12


    def get_lp_to_withdraw_given_token(self, lp_token, underlying_token, mantissa_underlying):
        # calc amount of `lp_token` to withdraw from pool to get `mantissa_underlying` of `underlying_token`
        # credit: https://github.com/Badger-Finance/badger-multisig/blob/a0eab1de153d99fd00bb696ba93ba1fab60a1266/scripts/issue/159/withdraw_9_digg_from_tcl.py
        x = Symbol('x')
        reserve_index = [lp_token.token0(), lp_token.token1()].index(underlying_token)
        return solve(
            (lp_token.getReserves()[reserve_index] * x / lp_token.totalSupply()) - mantissa_underlying, x
        )[0]


    def add_liquidity(self, tokenA, tokenB, mantissaA=None, mantissaB=None):
        # https://docs.uniswap.org/protocol/V2/reference/smart-contracts/router-02#addliquidity
        pair_address = self.factory.getPair(tokenA, tokenB)
        pair = self.safe.contract(pair_address)

        slp_balance = pair.balanceOf(self.safe)

        reserve0, reserve1, _ = pair.getReserves()

        path = [tokenA, tokenB]

        if mantissaA != None:
            path = [tokenA, tokenB]
            mantissaB = self.router.getAmountsOut(mantissaA, path)[1]

        else:
            path = [tokenB, tokenA]
            mantissaA = self.router.getAmountsOut(mantissaB, path)[1]

        # https://docs.uniswap.org/protocol/V2/reference/smart-contracts/library#quote
        quote_token0_min = self.router.quote(mantissaA, reserve0, reserve1)
        quote_token1_min = self.router.quote(mantissaB, reserve1, reserve0)

        tokenA.approve(self.router, mantissaA)
        tokenB.approve(self.router, mantissaB)

        amountA, amountB, liquidity = self.router.addLiquidity(
            tokenA,
            tokenB,
            mantissaA,
            mantissaB,
            quote_token1_min * (1 - self.max_slippage),
            quote_token0_min * (1 - self.max_slippage),
            self.safe.address,
            web3.eth.getBlock(web3.eth.blockNumber).timestamp + self.deadline,
        ).return_value

        assert (
            pair.balanceOf(self.safe)
            >= liquidity * (1 - self.max_slippage) + slp_balance
        )

    def remove_liquidity(self, slp, slp_amount, to_eth=False):
        # https://docs.uniswap.org/protocol/V2/reference/smart-contracts/router-02#swapexacttokensforeth
        slp.approve(self.router, slp_amount)

        tokenA = self.safe.contract(slp.token0())
        tokenB = self.safe.contract(slp.token1())

        balance_initial_tokenA = tokenA.balanceOf(self.safe)
        balance_initial_tokenB = tokenB.balanceOf(self.safe)

        expected_asset0 = slp.getReserves()[0] * slp_amount / slp.totalSupply()
        expected_asset1 = slp.getReserves()[1] * slp_amount / slp.totalSupply()

        received_asset0, received_asset1 = self.router.removeLiquidity(
            slp.token0(),
            slp.token1(),
            slp_amount,
            expected_asset0 * (1 - self.max_slippage),
            expected_asset1 * (1 - self.max_slippage),
            self.safe.address,
            web3.eth.getBlock(web3.eth.blockNumber).timestamp + self.deadline,
        ).return_value

        assert tokenA.balanceOf(
            self.safe
        ) >= balance_initial_tokenA + expected_asset0 * (1 - self.max_slippage)
        assert tokenB.balanceOf(
            self.safe
        ) >= balance_initial_tokenB + expected_asset1 * (1 - self.max_slippage)

        if to_eth:
            weth = interface.IWETH9(
                registry.eth.treasury_tokens.WETH, owner=self.safe.account
            )

            eth_initial_balance = self.safe.account.balance()

            weth.withdraw(received_asset1 * (1 - self.max_weth_unwrap))

            assert (
                self.safe.account.balance()
                >= eth_initial_balance + received_asset1 * (1 - self.max_weth_unwrap)
            )

    def swap_tokens_for_tokens(self, tokenIn, amountIn, path, recipient):
        # https://docs.uniswap.org/protocol/V2/reference/smart-contracts/router-02#swapexacttokensfortokens
        tokenOut = path[-1]
        balance_tokenOut = tokenOut.balanceOf(self.safe)

        amountOut = self.router.getAmountsOut(amountIn, path)[-1]
        tokenIn.approve(self.router, amountIn)

        self.router.swapExactTokensForTokens(
            amountIn,
            amountOut * (1 - self.max_slippage),
            path,
            recipient,
            web3.eth.getBlock(web3.eth.blockNumber).timestamp + self.deadline,
        )

        assert tokenOut.balanceOf(self.safe) >= balance_tokenOut + amountOut * (
            1 - self.max_slippage
        )

    def swap_exact_eth_for_tokens(self, amountIn, path, recipient):
        # https://docs.uniswap.org/protocol/V2/reference/smart-contracts/router-02#swapethforexacttokens
        tokenOut = path[-1]
        balance_tokenOut = tokenOut.balanceOf(self.safe)

        amountOut = self.router.getAmountsOut(amountIn, path)[-1]
        """
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
        """
        self.router.swapExactETHForTokens(
            amountOut * (1 - self.max_slippage),
            path,
            recipient,
            web3.eth.getBlock(web3.eth.blockNumber).timestamp + self.deadline,
            {"value": amountIn},
        )

        assert tokenOut.balanceOf(self.safe) >= balance_tokenOut + amountOut * (
            1 - self.max_slippage
        )

    def swap_exact_tokens_for_eth(self, tokenIn, amountIn, path, recipient):
        # https://docs.uniswap.org/protocol/V2/reference/smart-contracts/router-02#swapexacttokensforeth
        eth_initial_balance = self.safe.account.balance()
        amountOut = self.router.getAmountsOut(amountIn, path)[-1]

        tokenIn.approve(self.router, amountIn)

        self.router.swapExactTokensForETH(
            amountIn,
            amountOut * (1 - self.max_slippage),
            path,
            recipient,
            web3.eth.getBlock(web3.eth.blockNumber).timestamp + self.deadline,
        )

        assert self.safe.account.balance() >= eth_initial_balance + amountOut * (
            1 - self.max_slippage
        )
