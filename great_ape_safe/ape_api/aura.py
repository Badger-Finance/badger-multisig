from brownie import interface
from brownie.exceptions import VirtualMachineError

from great_ape_safe.ape_api.convex import Convex
from helpers.addresses import r


class Aura(Convex):
    def __init__(self, safe):
        self.safe = safe

        self.aura = interface.ERC20(r.treasury_tokens.AURA, owner=self.safe.account)
        self.aura_bal = interface.ERC20(
            r.treasury_tokens.AURABAL, owner=self.safe.account
        )

        # https://docs.aura.finance/developers/deployed-addresses
        self.booster = safe.contract(r.aura.booster)
        self.aura_locker = safe.contract(r.aura.vlAURA)
        self.aurabal_staking = safe.contract(r.aura.aurabal_staking)
        self.zap = safe.contract(r.aura.claim_zap)

    def _alert_not_relevant():
        print(" ==== NOT RELEVANT METHOD IN AURA CLASS ==== \n")


    def claim_all_from_booster(self):
        self.claim_all(1)


    def claim_all_from_locker(self):
        self.claim_all(2)


    def claim_all(self, option=1):
        # https://docs.convexfinance.com/convexfinanceintegration/baserewardpool
        # https://github.com/convex-eth/platform/blob/main/contracts/contracts/ClaimZap.sol#L103-L133
        # options param: https://etherscan.io/address/0x623b83755a39b12161a63748f3f595a530917ab2#code#F1#L42
        pending_rewards = []
        n_pools = self.booster.poolLength()

        if option == 1:
            for n in range(n_pools):
                _, _, _, rewards, _, _ = self.booster.poolInfo(n)
                if self.safe.contract(rewards).earned(self.safe) > 0:
                    pending_rewards.append(rewards)
            assert len(pending_rewards) > 0
            # in AURA the contracts has 8 arguments
            # https://etherscan.io/address/0x623b83755a39b12161a63748f3f595a530917ab2#code#F1#L118
            self.zap.claimRewards(pending_rewards, [], [], [], 0, 0, 0, option)
            for rewards in pending_rewards:
                reward_token = self.safe.contract(rewards).rewardToken()
                # this assert is a bit weak, but no starting balance is known since
                # we cannot know for which reward tokens contracts to check in the
                # beginning
                assert self.safe.contract(reward_token).balanceOf(self.safe) > 0
        elif option == 2:
            self.zap.claimRewards([], [], [], [], 0, 0, 0, option)

            # checkin five tokens, doubt will distribute ever more than that
            for i in range(5):
                try:
                    reward_token = self.aura_locker.rewardTokens(i)

                    assert self.safe.contract(reward_token).balanceOf(self.safe) > 0
                except VirtualMachineError:
                    return

    # methods which are not relevant in Aura architecture
    def get_pool_pid(self, _staking_token):
        self._alert_not_relevant()
        pass

    def create_vault(self, staking_token):
        self._alert_not_relevant()
        pass

    def stake_lock(self, staking_token, mantissa, seconds):
        self._alert_not_relevant()
        pass

    def withdraw_locked(self, staking_token, kek_id):
        self._alert_not_relevant()
        pass
