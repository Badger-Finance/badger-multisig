from datetime import datetime, timezone

from brownie import web3
from rich.console import Console
from helpers.addresses import registry


C = Console()


class Aave():
    def __init__(self, safe):
        self.safe       = safe
        # tokens
        self.aave       = safe.contract(registry.eth.treasury_tokens.AAVE)
        self.stkaave    = safe.contract(registry.eth.treasury_tokens.stkAAVE)
        # contracts
        self.controller = safe.contract(registry.eth.aave.incentives_controller)
        self.data       = safe.contract(registry.eth.aave.data_provider)
        self.pool       = safe.contract(registry.eth.aave.aave_lending_pool_v2)


    def deposit(self, underlying, mantissa, destination=None):
        # deposit `mantissa` amount of `underlying` into aave pool
        # https://docs.aave.com/developers/the-core-protocol/lendingpool#deposit
        destination = self.safe.address if not destination else destination
        atoken_addr = self.data.getReserveTokensAddresses(underlying)[0]
        atoken = self.safe.contract(atoken_addr)
        bal_before = atoken.balanceOf(destination)
        underlying.approve(self.pool, mantissa)
        self.pool.deposit(underlying, mantissa, destination, 0)
        assert atoken.balanceOf(destination) > bal_before


    def withdraw(self, underlying, mantissa, destination=None):
        # withdraw `underlying asset` from aave pool
        # https://docs.aave.com/developers/the-core-protocol/lendingpool#withdraw
        destination = self.safe.address if not destination else destination
        bal_before = underlying.balanceOf(destination)
        self.pool.withdraw(underlying, mantissa, destination)
        assert underlying.balanceOf(destination) > bal_before


    def withdraw_all(self, underlying, destination=None):
        # withdraw maximum balance of `underlying asset` from aave pool
        # https://docs.aave.com/developers/the-core-protocol/lendingpool#withdraw
        destination = self.safe.address if not destination else destination
        bal_before = underlying.balanceOf(destination)
        self.pool.withdraw(underlying, 2**256-1, destination)
        assert underlying.balanceOf(destination) > bal_before


    def claim_all(self, destination=None):
        # claim all pending rewards from the aave pool
        # https://docs.aave.com/developers/guides/liquidity-mining
        destination = self.safe.address if not destination else destination
        bal_before = self.stkaave.balanceOf(destination)
        pending = self.controller.getUserUnclaimedRewards(self.safe)
        assert pending > 0
        self.controller.claimRewards([], pending, destination)
        assert self.stkaave.balanceOf(destination) > bal_before


    def unstake_and_claim_all(self, destination=None):
        # unstake $stkaave into $aave and claim all rewards it accrued. if
        # cooldown hasn't been called yet, call it instead and report on exact
        # time window for when unstaking will available
        # https://docs.aave.com/developers/protocol-governance/staking-aave
        destination = self.safe.address if not destination else destination
        timestamp = web3.eth.getBlock(web3.eth.blockNumber).timestamp
        cooldown_called = self.stkaave.stakersCooldowns(self.safe)
        if cooldown_called > 0:
            threshold = cooldown_called + self.stkaave.COOLDOWN_SECONDS()
            deadline = threshold + self.stkaave.UNSTAKE_WINDOW()
            if timestamp <= threshold:
                # report exact unstaking window
                t0 = datetime.fromtimestamp(threshold).astimezone(timezone.utc)
                t0 = t0.strftime('%Y-%m-%d %H:%M:%S %Z')
                t1 = datetime.fromtimestamp(deadline).astimezone(timezone.utc)
                t1 = t1.strftime('%Y-%m-%d %H:%M:%S %Z')
                C.print(f'unstaking will be available between {t0} and {t1}\n')
                return
            elif timestamp <= deadline:
                bal_before = self.aave.balanceOf(destination)
                self.stkaave.redeem(destination, 2**256-1)
                assert self.aave.balanceOf(destination) > bal_before
                bal_before = self.aave.balanceOf(destination)
                self.stkaave.claimRewards(destination, 2**256-1)
                assert self.aave.balanceOf(destination) > bal_before
                return
        C.print('no valid window found; calling cooldown now...')
        self.stkaave.cooldown()
        self.unstake_and_claim(destination)
