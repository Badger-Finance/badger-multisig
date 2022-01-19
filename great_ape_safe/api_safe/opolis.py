from brownie import interface


class Opolis():
    def __init__(self, safe):
        self.safe = safe
        # have to use erc20 interface for proxy token
        self.work = interface.IERC20Metadata("0x6002410dDA2Fb88b4D0dc3c1D562F7761191eA80")
        self.staking_helper = safe.contract("0x8bF5aD0dBa1e29741740D96E55Bf27Aec30B18E2")
        self.whitelist = safe.contract("0x44a0487656420FDc15f9CA76dd95F3b8a2ef0Baa")
    
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

