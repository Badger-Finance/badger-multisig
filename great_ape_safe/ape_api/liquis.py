from brownie import interface
from brownie.exceptions import VirtualMachineError

from great_ape_safe.ape_api.convex import Convex
from helpers.addresses import r


class Liquis(Convex):
    def __init__(self, safe):
        self.safe = safe

        self.liq = interface.ERC20(r.treasury_tokens.LIQ, owner=self.safe.account)
        self.liq_lit = interface.ERC20(
            r.treasury_tokens.LIQLIT, owner=self.safe.account
        )

        # https://docs.liquis.app/
        self.booster = safe.contract(r.liquis.booster)
        self.liq_locker = safe.contract(r.liquis.vlLIQ)
        self.liqlit_staking = safe.contract(r.liquis.liquislit_staking)
        self.zap = safe.contract(r.liquis.claim_zap)
