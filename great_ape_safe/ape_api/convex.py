from brownie import interface

from helpers.addresses import registry


class VaultTypes:
    VAFRAX = 0
    UNIV2_TEMPLE = 1
    AFRAX = 2
    CURVE_LP = 3
    BADGER_FRAXBP = 33


class Convex:
    def __init__(self, safe):
        self.safe = safe

        # tokens
        self.cvx = interface.ERC20(
            registry.eth.treasury_tokens.CVX, owner=self.safe.account
        )
        self.cvxcrv = interface.ERC20(
            registry.eth.treasury_tokens.cvxCRV, owner=self.safe.account
        )

        # contracts
        self.booster = safe.contract(registry.eth.convex.booster)
        self.zap = safe.contract(registry.eth.convex.claim_zap)
        self.cvx_extra_rewards = interface.ICvxExtraRewards(
            registry.eth.convex.vlCvxExtraRewardDistribution, owner=self.safe.account
        )

        # frax contract section
        self.frax_booster = safe.contract(registry.eth.convex.frax.booster)
        self.frax_pool_registry = safe.contract(registry.eth.convex.frax.pool_registry)

    def get_pool_info(self, underlying):
        # return pool id, cvx_token and gauge address for `underlying`
        # https://docs.convexfinance.com/convexfinanceintegration/booster#pool-info
        n_pools = self.booster.poolLength()
        for n in range(n_pools):
            lptoken, token, gauge, rewards, _, _ = self.booster.poolInfo(n)
            if lptoken == underlying.address:
                return n, token, gauge, rewards

    def deposit(self, underlying, mantissa):
        # deposit `mantissa` amount of `underlying` into its respective convex pool
        # https://docs.convexfinance.com/convexfinanceintegration/booster#deposits
        stake = 0
        pool_id = self.get_pool_info(underlying)[0]
        underlying.approve(self.booster, mantissa)
        assert self.booster.deposit(pool_id, mantissa, stake).return_value == True

    def deposit_and_stake(self, underlying, mantissa):
        # deposit `mantissa` amount of `underlying` into its respective convex pool
        # and stake it into convex's gauge
        # https://docs.convexfinance.com/convexfinanceintegration/booster#deposits
        stake = 1
        pool_id = self.get_pool_info(underlying)[0]
        underlying.approve(self.booster, mantissa)
        assert self.booster.deposit(pool_id, mantissa, stake).return_value == True

    def deposit_all(self, underlying):
        # deposit complete balance of `underlying` into its respective convex pool
        # https://docs.convexfinance.com/convexfinanceintegration/booster#deposits
        stake = 0
        pool_id = self.get_pool_info(underlying)[0]
        underlying.approve(self.booster, 2**256 - 1)
        assert self.booster.depositAll(pool_id, stake).return_value == True
        underlying.approve(self.booster, 0)

    def deposit_all_and_stake(self, underlying):
        # deposit complete balance of `underlying` into its respective convex pool
        # and stake it into convex's gauge
        # https://docs.convexfinance.com/convexfinanceintegration/booster#deposits
        stake = 1
        pool_id = self.get_pool_info(underlying)[0]
        underlying.approve(self.booster, 2**256 - 1)
        assert self.booster.depositAll(pool_id, stake).return_value == True
        underlying.approve(self.booster, 0)

    def withdraw(self, underlying, mantissa):
        # withdraw `mantissa` amount of `underlying` from its respective convex pool
        # https://docs.convexfinance.com/convexfinanceintegration/booster#withdrawals
        pool_id = self.get_pool_info(underlying)[0]
        assert self.booster.withdraw(pool_id, mantissa).return_value == True

    def withdraw_all(self, underlying):
        # withdraw complete balance of `underlying` from its respective convex pool
        # https://docs.convexfinance.com/convexfinanceintegration/booster#withdrawals
        pool_id = self.get_pool_info(underlying)[0]
        assert self.booster.withdrawAll(pool_id).return_value == True

    def claim_all(self):
        # https://docs.convexfinance.com/convexfinanceintegration/baserewardpool
        # https://github.com/convex-eth/platform/blob/main/contracts/contracts/ClaimZap.sol#L103-L133
        pending_rewards = []
        n_pools = self.booster.poolLength()
        for n in range(n_pools):
            lptoken, token, gauge, rewards, _, _ = self.booster.poolInfo(n)
            if self.safe.contract(rewards).earned(self.safe) > 0:
                pending_rewards.append(rewards)
        assert len(pending_rewards) > 0
        self.zap.claimRewards(pending_rewards, [], [], [], 0, 0, 0, 0, 0)
        for rewards in pending_rewards:
            reward_token = self.safe.contract(rewards).rewardToken()
            # this assert is a bit weak, but no starting balance is known since
            # we cannot know for which reward tokens contracts to check in the
            # beginning
            assert self.safe.contract(reward_token).balanceOf(self.safe) > 0

    def stake(self, underlying, mantissa, destination=None):
        # stake `mantissa` amount of `underlying`'s corresponding convex tokens
        # into convex's gauge
        # https://docs.convexfinance.com/convexfinanceintegration/baserewardpool#stake-deposit-tokens
        _, cvx_token, _, rewards = self.get_pool_info(underlying)
        self.safe.contract(cvx_token).approve(rewards, mantissa)
        if destination:
            assert (
                self.safe.contract(rewards).stakeFor(destination, mantissa).return_value
                == True
            )
        else:
            assert self.safe.contract(rewards).stake(mantissa).return_value == True

    def stake_all(self, underlying):
        # stake complete balance of `underlying`'s corresponding convex tokens
        # https://docs.convexfinance.com/convexfinanceintegration/baserewardpool#stake-deposit-tokens
        _, cvx_token, _, rewards = self.get_pool_info(underlying)
        self.safe.contract(cvx_token).approve(rewards, 2**256 - 1)
        assert self.safe.contract(rewards).stakeAll().return_value == True
        self.safe.contract(cvx_token).approve(rewards, 0)

    def unstake(self, underlying, mantissa, claim=1):
        # unstake `mantissa` amount of corresponding cvx_tokens for `underlying`
        # automatically also claims its outstanding rewards (set to 0 to not claim)
        # https://docs.convexfinance.com/convexfinanceintegration/baserewardpool#unstake-withdraw-tokens
        _, cvx_token, _, rewards = self.get_pool_info(underlying)
        bal_before = self.safe.contract(cvx_token).balanceOf(self.safe)
        self.safe.contract(rewards).withdraw(mantissa, claim)
        assert self.safe.contract(cvx_token).balanceOf(self.safe) > bal_before

    def unstake_all(self, underlying, claim=1):
        # unstake complete balance of corresponding cvx_tokens for `underlying`
        # automatically also claims its outstanding rewards (set to 0 to not claim)
        # https://docs.convexfinance.com/convexfinanceintegration/baserewardpool#unstake-withdraw-tokens
        _, cvx_token, _, rewards = self.get_pool_info(underlying)
        bal_before = self.safe.contract(cvx_token).balanceOf(self.safe)
        self.safe.contract(rewards).withdrawAll(claim)
        assert self.safe.contract(cvx_token).balanceOf(self.safe) > bal_before

    def unstake_and_withdraw(self, underlying, mantissa, claim=1):
        # unstake `mantissa` amount of corresponding cvx_tokens for `underlying`
        # and unwrap those cvx_tokens back to the `underlying`
        # automatically also claims its outstanding rewards (set to 0 to not claim)
        # https://docs.convexfinance.com/convexfinanceintegration/baserewardpool#unstake-withdraw-tokens
        _, _, _, rewards = self.get_pool_info(underlying)
        assert (
            self.safe.contract(rewards).withdrawAndUnwrap(mantissa, claim).return_value
            == True
        )

    def unstake_all_and_withdraw_all(self, underlying, claim=1):
        # unstake complete balance of corresponding cvx_tokens for `underlying`
        # and unwrap those cvx_tokens back to the `underlying`
        # automatically also claims its outstanding rewards (set to 0 to not claim)
        # https://docs.convexfinance.com/convexfinanceintegration/baserewardpool#unstake-withdraw-tokens
        _, _, _, rewards = self.get_pool_info(underlying)
        bal_before = underlying.balanceOf(self.safe)
        self.safe.contract(rewards).withdrawAllAndUnwrap(claim)
        assert underlying.balanceOf(self.safe) > bal_before

    def get_pool_pid(self, _staking_token):
        len = self.frax_pool_registry.poolLength()

        for i in range(len):
            _, _, staking_token, _, _ = self.frax_pool_registry.poolInfo(i)
            if _staking_token == staking_token:
                return i

    def get_vault(self, staking_token, owner=None):
        owner = self.safe.address if not owner else owner
        pid = self.get_pool_pid(staking_token)

        return self.frax_pool_registry.vaultMap(pid, owner)

    def create_vault(self, staking_token):
        pid = self.get_pool_pid(staking_token)
        # internally happens the approval of the staking_token for the staking_address
        # ref: https://github.com/convex-eth/frax-cvx-platform/blob/main/contracts/contracts/StakingProxyERC20.sol#L34
        self.frax_booster.createVault(pid)

    def stake_lock(self, staking_token, mantissa, seconds):
        pid = self.get_pool_pid(staking_token)

        if pid in [VaultTypes.AFRAX, VaultTypes.BADGER_FRAXBP]:
            staking_proxy = self.safe.contract(self.get_vault(staking_token))
            staking_contract = self.safe.contract(staking_proxy.stakingAddress())
            staking_token.approve(staking_proxy, mantissa)

            lock_time_min = staking_contract.lock_time_min()
            lock_time_for_max_multiplier = (
                staking_contract.lock_time_for_max_multiplier()
            )

            assert seconds >= lock_time_min and seconds <= lock_time_for_max_multiplier

            initial_locked_liq = staking_contract.lockedLiquidityOf(staking_proxy)

            # kek_id is returned: https://etherscan.io/address/0x02577b426f223a6b4f2351315a19ecd6f357d65c#code#L2466
            # but depends on block.timestamp, so not much value tracking it on the return
            staking_proxy.stakeLocked(mantissa, seconds)

            assert (
                staking_contract.lockedLiquidityOf(staking_proxy) > initial_locked_liq
            )

    def withdraw_locked(self, staking_token, kek_id):
        pid = self.get_pool_pid(staking_token)

        if pid == VaultTypes.AFRAX:
            staking_proxy = self.safe.contract(self.get_vault(staking_token))
            staking_contract = self.safe.contract(staking_proxy.stakingAddress())

            rewards = staking_contract.getAllRewardTokens()

            balances_rewards_before = [
                self.safe.contract(reward).balanceOf(self.safe) for reward in rewards
            ]

            balance_staking_token_before = staking_token.balanceOf(self.safe)

            staking_proxy.withdrawLocked(kek_id)

            assert staking_token.balanceOf(self.safe) > balance_staking_token_before

            assert any(
                [
                    self.safe.contract(reward).balanceOf(self.safe) > balance
                    for balance, reward in zip(balances_rewards_before, rewards)
                ]
            )
