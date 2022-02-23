from brownie import accounts, interface, web3
from helpers.addresses import registry


class UniV2:
    def __init__(self, safe):
        self.safe = safe

        self.router = safe.contract(registry.eth.uniswap.routerV2)
        self.factory = safe.contract(registry.eth.uniswap.factoryV2)

        self.max_slippage = 0.02
        self.max_weth_unwrap = 0.01
        self.deadline = 60 * 60 * 12


    def add_liquidity(self, tokenA, tokenB, mantissaA=None, mantissaB=None, destination=None):
        # https://docs.uniswap.org/protocol/V2/reference/smart-contracts/router-02#addliquidity
        destination = self.safe.address if not destination else destination

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
            destination,
            web3.eth.getBlock(web3.eth.blockNumber).timestamp + self.deadline,
        ).return_value

        assert (
            pair.balanceOf(destination)
            >= liquidity * (1 - self.max_slippage) + slp_balance
        )


    def remove_liquidity(self, slp, slp_amount, destination=None, to_eth=False):
        # https://docs.uniswap.org/protocol/V2/reference/smart-contracts/router-02#swapexacttokensforeth
        destination = self.safe.address if not destination else destination

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
            destination,
            web3.eth.getBlock(web3.eth.blockNumber).timestamp + self.deadline,
        ).return_value

        assert tokenA.balanceOf(
            destination
        ) >= balance_initial_tokenA + expected_asset0 * (1 - self.max_slippage)
        assert tokenB.balanceOf(
            destination
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


    def swap_tokens_for_tokens(self, tokenIn, amountIn, path, destination=None):
        # https://docs.uniswap.org/protocol/V2/reference/smart-contracts/router-02#swapexacttokensfortokens
        destination = self.safe.address if not destination else destination

        tokenOut = path[-1]
        balance_tokenOut = tokenOut.balanceOf(self.safe)

        amountOut = self.router.getAmountsOut(amountIn, path)[-1]
        tokenIn.approve(self.router, amountIn)

        self.router.swapExactTokensForTokens(
            amountIn,
            amountOut * (1 - self.max_slippage),
            path,
            destination,
            web3.eth.getBlock(web3.eth.blockNumber).timestamp + self.deadline,
        )

        assert (
            tokenOut.balanceOf(destination)
            >= balance_tokenOut + amountOut * (1 - self.max_slippage)
        )


    def swap_exact_eth_for_tokens(self, amountIn, path, destination=None):
        # https://docs.uniswap.org/protocol/V2/reference/smart-contracts/router-02#swapethforexacttokens
        destination = self.safe.address if not destination else destination

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
            destination,
            web3.eth.getBlock(web3.eth.blockNumber).timestamp + self.deadline,
            {"value": amountIn},
        )

        assert (
            tokenOut.balanceOf(destination)
            >= balance_tokenOut + amountOut * (1 - self.max_slippage)
        )


    def swap_exact_tokens_for_eth(self, tokenIn, amountIn, path, destination=None):
        # https://docs.uniswap.org/protocol/V2/reference/smart-contracts/router-02#swapexacttokensforeth
        destination = self.safe.address if not destination else destination

        eth_initial_balance = self.safe.account.balance()
        amountOut = self.router.getAmountsOut(amountIn, path)[-1]

        tokenIn.approve(self.router, amountIn)

        self.router.swapExactTokensForETH(
            amountIn,
            amountOut * (1 - self.max_slippage),
            path,
            destination,
            web3.eth.getBlock(web3.eth.blockNumber).timestamp + self.deadline,
        )

        assert (
            accounts.at(destination, force=True).balance()
            >= eth_initial_balance + amountOut * (1 - self.max_slippage)
        )
