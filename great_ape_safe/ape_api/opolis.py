from brownie import interface
from helpers.addresses import registry


class Opolis():
    def __init__(self, safe):
        self.safe = safe
        # have to use erc20 interface for proxy token
        self.work = interface.ERC20(registry.poly.coingecko_tokens.WORK)
        self.staking_helper = safe.contract(registry.poly.opolis.stakingHelper)
        self.whitelist = safe.contract(registry.poly.opolis.whitelist)


    def stake(self, mantissas):
        # stake `mantissa` amount of `WORK` into staking helper contract
        self.work.approve(self.staking_helper, mantissas, {'from': self.safe.address})
        bal_before = self.work.balanceOf(self.safe)
        self.staking_helper.stake(mantissas)
        assert self.work.balanceOf(self.safe) < bal_before


    def unstake(self, mantissas):
        # unstake `mantissa` amount of `WORK` from staking helper contract
        bal_before = self.work.balanceOf(self.safe)
        self.staking_helper.unstake(mantissas)
        assert self.work.balanceOf(self.safe) > bal_before
