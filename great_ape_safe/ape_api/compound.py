from helpers.addresses import registry

from brownie import interface


class Compound:
    def __init__(self, safe):
        self.safe = safe
        # tokens
        self.comp = safe.contract(registry.eth.treasury_tokens.COMP)
        # contracts
        self.comptroller = safe.contract(registry.eth.compound.comptroller)

    def deposit(self, underlying, mantissa):
        # deposit `mantissa` amount of `underlying` into its respective compound's ctoken
        # https://compound.finance/docs/ctokens#mint
        for ctoken in self.comptroller.getAllMarkets():
            ctoken = interface.ICErc20Delegate(ctoken, owner=self.safe.account)
            try:
                if ctoken.underlying() == underlying.address:
                    if self.comptroller.mintGuardianPaused(ctoken):
                        # eg old cwbtc contract has been replaced by cwbtc2
                        continue
                    underlying.approve(ctoken, mantissa)
                    assert ctoken.mint(mantissa).return_value == 0
                    return
            except (AttributeError, ValueError):
                # $ceth has no underlying
                if ctoken.symbol() == "cETH":
                    pass
                else:
                    # in case `AttributeError` stems from something else
                    raise
        # for loop did not find `underlying`
        raise

    def deposit_eth(self, mantissa):
        # deposit `mantissa` amount of $eth into its respective compound's ctoken
        # https://compound.finance/docs/ctokens#mint
        for ctoken in self.comptroller.getAllMarkets():
            ctoken = interface.ICErc20Delegate(ctoken, owner=self.safe.account)
            if ctoken.symbol() == "cETH":
                bal_before = ctoken.balanceOf(self.safe)
                ctoken.mint({"from": self.safe.address, "value": mantissa})
                assert ctoken.balanceOf(self.safe) > bal_before
                return
        # for loop did not find $ceth
        raise

    def withdraw(self, underlying, mantissa):
        # withdraw `mantissa` amount of `underlying` from its corresponding ctoken
        # https://compound.finance/docs/ctokens#redeem-underlying
        for ctoken in self.comptroller.getAllMarkets():
            ctoken = interface.ICErc20Delegate(ctoken, owner=self.safe.account)
            try:
                if ctoken.underlying() == underlying.address:
                    assert ctoken.redeemUnderlying(mantissa).return_value == 0
                    return
            except (AttributeError, ValueError):
                # $ceth has no underlying
                if ctoken.symbol() == "cETH":
                    pass
                else:
                    # in case `AttributeError` stems from something else
                    raise
        # for loop did not find `underlying`
        raise

    def withdraw_eth(self, mantissa):
        # withdraw `mantissa` amount of $eth from its corresponding ctoken
        # https://compound.finance/docs/ctokens#redeem-underlying
        for ctoken in self.comptroller.getAllMarkets():
            ctoken = interface.ICErc20Delegate(ctoken, owner=self.safe.account)
            if ctoken.symbol() == "cETH":
                assert ctoken.redeemUnderlying(mantissa).return_value == 0
                return
        # for loop did not find $ceth
        raise

    def withdraw_ctoken(self, ctoken, mantissa):
        # redeem `mantissa` amount of `ctoken` back into its underlying
        # https://compound.finance/docs/ctokens#redeem
        assert ctoken.redeem(mantissa).return_value == 0

    def claim_all(self):
        # claim all $comp accrued by safe in all markets
        # https://compound.finance/docs/comptroller#claim-comp

        bal_before = self.comp.balanceOf(self.safe)
        self.comptroller.claimComp(self.safe)
        assert self.comp.balanceOf(self.safe) > bal_before

    def claim(self, underlyings):
        # convert each `underlying` in list `underlyings` to its corresponding
        # ctoken and claim all pending $comp for those ctokens in one call
        # instead of a list `underlyings` can also be a single asset
        # https://compound.finance/docs/comptroller#claim-comp
        if type(underlyings) != "list":
            underlyings = [underlyings]
        ctokens = []
        for underlying in underlyings:
            for ctoken in self.comptroller.getAllMarkets():
                ctoken = interface.ICErc20Delegate(ctoken, owner=self.safe.account)
                try:
                    if ctoken.underlying() == underlying.address:
                        ctokens.append(ctoken.address)
                        break
                except (AttributeError, ValueError):
                    if ctoken.symbol() == "cETH":
                        # $ceth has no underlying
                        pass
                    else:
                        # in case `AttributeError` stems from something else
                        raise
        assert len(ctokens) > 0
        bal_before = self.comp.balanceOf(self.safe)
        self.comptroller.claimComp(self.safe, ctokens)
        assert self.comp.balanceOf(self.safe) > bal_before
