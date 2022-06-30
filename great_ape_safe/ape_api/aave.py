from datetime import datetime, timezone
from re import L

from brownie import web3
from rich.console import Console
from helpers.addresses import registry


C = Console()


class Aave():
    def __init__(self, safe):
        self.safe = safe

        # tokens
        self.aave = safe.contract(registry.eth.treasury_tokens.AAVE)
        self.stkaave = safe.contract(registry.eth.treasury_tokens.stkAAVE)

        # contracts
        self.controller = safe.contract(registry.eth.aave.incentives_controller)
        self.data = safe.contract(registry.eth.aave.data_provider)
        self.pool = safe.contract(registry.eth.aave.aave_lending_pool_v2)
        self.oracle = safe.contract(registry.eth.aave.price_oracle_v2)


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


    def claim_all(self, markets=[], destination=None):
        # claim all pending rewards from the aave pool
        # https://docs.aave.com/developers/guides/liquidity-mining
        destination = self.safe.address if not destination else destination
        bal_before = self.stkaave.balanceOf(destination)
        # https://docs.aave.com/developers/v/2.0/guides/liquidity-mining#getuserunclaimedrewards
        pending_from_last_action = self.controller.getUserUnclaimedRewards(self.safe)
        # https://docs.aave.com/developers/v/2.0/guides/liquidity-mining#getrewardsbalance
        pending_from_assets = self.controller.getRewardsBalance(markets, self.safe.address)
        assert pending_from_last_action > 0 or pending_from_assets > 0
        pending = pending_from_last_action if pending_from_last_action > 0 else pending_from_assets
        self.controller.claimRewards(markets, pending, destination)
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


    def borrow(self, underlying, mantissa, variable_rate=True):
        mode = 2 if variable_rate else 1
        self.pool.borrow(underlying, mantissa, mode, 0, self.safe.address)


    def repay(self, underlying, mantissa, variable_rate=True):
        mode = 2 if variable_rate else 1
        underlying.approve(self.pool, mantissa)
        self.pool.repay(underlying, mantissa, mode, self.safe.address)


    def repay_all(self, underlying, variable_rate=True):
        mode = 2 if variable_rate else 1
        underlying.approve(self.pool, 2**256-1)
        self.pool.repay(underlying, 2**256-1, mode, self.safe.address)
        underlying.approve(self.pool, 0)


    def _get_debt_in_token(self, token):
        info = self.pool.getUserAccountData(self.safe.address)
        debt_in_eth = info[1]
        token_to_eth_rate = self.oracle.getAssetPrice(token)
        return (debt_in_eth * 10 ** token.decimals()) / token_to_eth_rate


    def lever_up(self, collateral_token, borrow_token, perc):
        '''
        given total borrow amounts in the aave user account, we will use
        `percent_bps` of it to borrow `borrow_token`
        '''
        ## get total borrowable
        info = self.pool.getUserAccountData(self.safe.address)

        # make sure we do not want to borrow more than max ltv
        ltv = info[4] / 10_000
        assert perc <= ltv

        # calc available borrows expressed in `borrow_token`
        available_borrows_eth = info[2]
        borrow_to_eth_rate = self.oracle.getAssetPrice(borrow_token)
        we_want_to_borrow = available_borrows_eth / borrow_to_eth_rate * perc / ltv
        we_want_to_borrow *= 1.01  # correct for slippage and swap fee
        we_want_to_borrow *= 10 ** borrow_token.decimals()

        # borrow
        self.borrow(borrow_token, we_want_to_borrow)

        # swap borrowed for more `collateral_token` and deposit back into aave
        # TODO: add swap functions to uni_v3 class and use that instead
        self.safe.init_sushi()
        to_reinvest = self.safe.sushi.swap_tokens_for_tokens(
            borrow_token,
            we_want_to_borrow,
            [borrow_token, registry.eth.treasury_tokens.WETH, collateral_token]
        )[-1]
        self.deposit(collateral_token, to_reinvest)


    def delever(self, collateral_token, borrow_token):
        debt_to_repay = self._get_debt_in_token(borrow_token)
        debt_paid = 0
        while debt_paid < debt_to_repay:
            ## Given amount of debt_to_repay, withdraw what is possible and repay
            collateral_in_eth, debt_in_eth, available_borrows_eth, liq_threshold, _, _ = self.pool.getUserAccountData(self.safe)
            borrow_to_eth_rate = self.oracle.getAssetPrice(borrow_token)
            collateral_to_eth_rate = self.oracle.getAssetPrice(collateral_token)
            max_to_withdraw = (debt_to_repay * borrow_to_eth_rate * 10**collateral_token.decimals()) / (collateral_to_eth_rate * 10**borrow_token.decimals())

            ## How much `collateral_token` do we need to withdraw, to repay this debt?
            available_withdraw_eth = available_borrows_eth * 10_000 / liq_threshold
            assert 0 < available_withdraw_eth and available_withdraw_eth <= collateral_in_eth
            available_to_withdraw = available_withdraw_eth * 10 ** collateral_token.decimals() / collateral_to_eth_rate

            ## Cap withdrawal to maximum required for debt_to_repay
            available_to_withdraw = min(available_to_withdraw, max_to_withdraw)

            ## This loop might withdraw a bit more than required for small residues of debt
            ## Add some buffer (5%) for swap slippage/fee etc
            available_to_withdraw *= 1.05

            ## Cap withdrawal to maximum collateral deposited
            max_deposited = (collateral_in_eth - debt_in_eth) * 10 ** collateral_token.decimals() / collateral_to_eth_rate
            available_to_withdraw = min(available_to_withdraw, max_deposited)

            ## Withdraw
            self.withdraw(collateral_token, available_to_withdraw)

            bal_borrow_token_before = borrow_token.balanceOf(self.safe)

            ## Swap to debt
            self.safe.init_sushi()
            to_repay = self.safe.sushi.swap_tokens_for_tokens(
                collateral_token,
                available_to_withdraw,
                [collateral_token, registry.eth.treasury_tokens.WETH, borrow_token]
            )[-1]

            ## Repay
            self.repay(borrow_token, to_repay)
            debt_paid = debt_paid + to_repay

        bal_borrow_token_after = borrow_token.balanceOf(self.safe)

        ## Swap remaining margin of borrow token back into collateral token
        self.safe.init_sushi()
        self.safe.sushi.swap_tokens_for_tokens(
            borrow_token,
            bal_borrow_token_after - bal_borrow_token_before,
            [borrow_token, registry.eth.treasury_tokens.WETH, collateral_token]
        )

        assert self._get_debt_in_token(borrow_token) == 0
