import numpy as np
from brownie import chain, interface


class Saddle():
    """
    https://docs.saddle.finance/contracts
    https://github.com/saddle-finance/saddle-contract/tree/master/contracts/interfaces
    """
    def __init__(self, safe):
        self.safe = safe
        # tokens
        self.sdl = interface.IERC20Metadata (
            '0xf1Dc500FdE233A4055e25e5BbF516372BC4F6871',
            owner=self.safe.account
        )
        self.aleth_pool = interface.ISwap(
            '0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a', owner=safe.account
        )
        self.aleth_token = interface.ILPToken(
            '0xc9da65931ABf0Ed1b74Ce5ad8c041C4220940368', owner=safe.account
        )
        self.d4_pool = interface.ISwap(
            '0xC69DDcd4DFeF25D8a793241834d4cc4b3668EAD6', owner=safe.account
        )
        self.d4_token = interface.ILPToken(
            '0xd48cF4D7FB0824CC8bAe055dF3092584d0a1726A', owner=safe.account
        )
        # parameters
        self.deadline = 60 * 60 * 12  # 12 hours
        self.max_slippage_and_fees = .02


    def deposit(self, lp_token, mantissas, asset=None):
        # wrap `mantissas` of underlying tokens into a saddle `lp_token`
        # `mantissas` do not need to be balanced in any way
        # if `mantissas` is not a list but an int, `asset` needs to be specified
        # as well, in order to automatically determine correct slot number
        # https://docs.saddle.finance/solidity-docs/swap#swap-addliquidity-uint256-uint256-uint256
        pool_addr = lp_token.owner()
        pool = interface.ISwap(pool_addr, owner=self.safe.account)

        if type(mantissas) is int and asset is not None:
            mantissa = mantissas
            assert mantissa > 0
            index = pool.getTokenIndex(asset)
            n_coins = len(pool.calculateRemoveLiquidity(0))
            mantissas = list(np.zeros(n_coins))
            mantissas[index] = mantissa
            # make sure we found the right slot and populated it
            assert (np.array(mantissas) > 0).any()
        expected = pool.calculateTokenAmount(mantissas, True)
        # approve for assets corresponding to mantissas
        for i, mantissa in enumerate(mantissas):
            if mantissa > 0:
                asset = interface.IERC20Metadata(
                    pool.getToken(i), owner=self.safe.account
                )
                asset.approve(pool, mantissa)

        bal_before = lp_token.balanceOf(self.safe)
        pool.addLiquidity(
            mantissas,
            expected * (1 - self.max_slippage_and_fees),
            chain.time() + self.deadline
        )
        assert lp_token.balanceOf(self.safe) > bal_before


    def withdraw(self, lp_token, mantissa):
        # unwrap `mantissa` amount of lp_token back to its underlyings
        # (in same ratio as pool is currently in)
        # https://docs.saddle.finance/solidity-docs/swap#swap-removeliquidity-uint256-uint256-uint256
        pool_addr = lp_token.owner()
        pool = interface.ISwap(pool_addr, owner=self.safe.account)

        expected = np.array(pool.calculateRemoveLiquidity(mantissa))
        minima = list(expected * (1 - self.max_slippage_and_fees))

        lp_token.approve(pool, mantissa)
        receivables = pool.removeLiquidity(
            mantissa, minima, chain.time() + self.deadline
        ).return_value
        assert (np.array(receivables) > 0).all()


    def withdraw_to_one_coin(self, lp_token, mantissa, asset):
        # unwrap `mantissa` amount of `lp_token` but single sided; into `asset`
        # https://docs.saddle.finance/solidity-docs/swap#swap-removeliquidityonetoken-uint256-uint8-uint256-uint256
        pool_addr = lp_token.owner()
        pool = interface.ISwap(pool_addr, owner=self.safe.account)

        index = pool.getTokenIndex(asset)
        expected = pool.calculateRemoveLiquidityOneToken(mantissa, index)
        minimum = expected * (1 - self.max_slippage_and_fees)

        lp_token.approve(pool, mantissa)
        receivable = pool.removeLiquidityOneToken(
            mantissa, index, minimum, chain.time() + self.deadline
        ).return_value

        assert receivable > 0
