from brownie import interface, Wei
from helpers.addresses import registry

class Rari():
    def __init__(self, safe):
        self.safe = safe

        # contracts
        self.unitroller = interface.IRariComptroller(
            registry.eth.rari.unitroller, owner=self.safe.account
        )


    def ftoken_is_paused(self, ftoken_addr):
        return self.unitroller.borrowGuardianPaused(ftoken_addr)


    def ftoken_pause(self, ftoken_addr, rf=None):
        self.unitroller._setBorrowPaused(ftoken_addr, True)
        if rf is not None:
            if self.ftoken_get_rf(ftoken_addr) != rf:
                self.ftoken_set_rf(ftoken_addr, rf)
        assert self.ftoken_is_paused(ftoken_addr)


    def ftoken_unpause(self, ftoken_addr, rf=None):
        self.unitroller._setBorrowPaused(ftoken_addr, False)
        if rf is not None:
            if self.ftoken_get_rf() != rf:
                self.ftoken_set_rf(ftoken_addr, rf)
        assert self.ftoken_is_paused(ftoken_addr) is False


    def ftoken_is_listed(self, ftoken_addr):
        is_listed, _ = self.unitroller.markets(ftoken_addr)
        return is_listed


    def ftoken_get_rf(self, ftoken_addr):
        ftoken = interface.IFToken(ftoken_addr, owner=self.safe.account)
        return ftoken.reserveFactorMantissa() / 1e18


    def ftoken_set_rf(self, ftoken_addr, rf):
        ftoken = interface.IFToken(ftoken_addr, owner=self.safe.account)
        ftoken._setReserveFactor(rf * 1e18)
        assert self.ftoken_get_rf(ftoken_addr) == rf


    def ftoken_get_cf(self, ftoken_addr):
        _, cf_mantissa = self.unitroller.markets(ftoken_addr)
        return cf_mantissa / 1e18


    def ftoken_set_cf(self, ftoken_addr, cf):
        self.unitroller._setCollateralFactor(ftoken_addr, cf * 1e18)
        assert self.ftoken_get_cf(ftoken_addr) == cf


    def ftoken_get_rate_model(self, ftoken_addr):
        ftoken = interface.IFToken(ftoken_addr, owner=self.safe.account)
        return ftoken.interestRateModel()


    def ftoken_set_rate_model(self, ftoken_addr, rate_model_addr):
        ftoken = interface.IFToken(ftoken_addr, owner=self.safe.account)
        ftoken._setInterestRateModel(rate_model_addr)
        assert self.ftoken_get_rate_model(ftoken_addr) == rate_model_addr


    def ftoken_get_admin_fee(self, ftoken_addr):
        ftoken = interface.IFToken(ftoken_addr, owner=self.safe.account)
        return ftoken.adminFeeMantissa() / 1e18


    def ftoken_set_admin_fee(self, ftoken_addr, admin_fee):
        ftoken = interface.IFToken(ftoken_addr, owner=self.safe.account)
        ftoken._setAdminFee(admin_fee * 1e18)
        assert self.ftoken_get_admin_fee(ftoken_addr) == admin_fee


    def get_liquidation_incentive(self):
        return self.unitroller.liquidationIncentiveMantissa() / 1e18


    def set_liquidation_incentive(self, new_incentive):
        assert self.get_liquidation_incentive() != new_incentive
        self.unitroller._setLiquidationIncentive(Wei(f"{new_incentive} ether"))
        assert self.get_liquidation_incentive() == new_incentive


    def add_ftoken_to_pool(self, ftoken_addr, cf=None):
        assert ftoken_addr not in self.unitroller.getAllMarkets()
        if cf:
            self.unitroller._supportMarketAndSetCollateralFactor(ftoken_addr, cf * 1e18)
        else:
            self.unitroller._supportMarket(ftoken_addr)
        assert ftoken_addr in self.unitroller.getAllMarkets()


    def upgrade_comptroller(self, implementation):
        self.unitroller._setPendingImplementation(implementation)
        assert self.unitroller.pendingComptrollerImplementation() == implementation
        comptroller = interface.IRariComptroller(
            implementation, owner=self.safe.account
        )
        comptroller._become(self.unitroller.address)
        assert self.unitroller.comptrollerImplementation() == implementation


    def upgrade_ftoken(self, ftoken_addr, implementation, allow_resign=False):
        ftoken = interface.IFToken(ftoken_addr, owner=self.safe.account)
        ftoken._setImplementation(implementation, allow_resign, b'')
        assert ftoken.implementation() == implementation


    def set_pause_guardian(self, new_guardian):
        self.unitroller._setPauseGuardian(new_guardian)
        assert self.unitroller.pauseGuardian() == new_guardian


    def set_borrow_guardian(self, new_guardian):
        self.unitroller._setBorrowCapGuardian(new_guardian)
        assert self.unitroller.borrowCapGuardian() == new_guardian


    def set_market_supply_caps(self, ftoken_addresses, new_supply_caps):
        self.unitroller._setMarketSupplyCaps(ftoken_addresses, new_supply_caps)
        for index, ftoken_addr in enumerate(ftoken_addresses):
            assert self.unitroller.supplyCaps(ftoken_addr) == new_supply_caps[index]