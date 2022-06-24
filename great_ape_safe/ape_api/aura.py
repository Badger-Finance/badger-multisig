from brownie import interface
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

    def _alert_not_relevant():
        print(" ==== NOT RELEVANT METHOD IN AURA CLASS ==== \n")

    # methods which are not relevant in Aura architecture
    def claim_all(self):
        self._alert_not_relevant()
        pass

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
