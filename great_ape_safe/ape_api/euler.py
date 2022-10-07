from brownie import interface
from rich.console import Console
from helpers.addresses import r


C = Console()


class Euler:
    def __init__(self, safe):
        self.safe = safe
        self.euler = safe.contract(r.euler.euler)
        self.markets = interface.IEuler(r.euler.euler_markets, owner=safe.account)

    def deposit(self, underlying, amount):
        etoken = interface.IEToken(
            self.markets.underlyingToEToken(underlying), owner=self.safe.account
        )

        before_etoken = etoken.balanceOf(self.safe)
        before_underlying = underlying.balanceOf(self.safe)

        underlying.approve(self.euler, amount)
        etoken.deposit(0, amount)

        after_etoken = etoken.balanceOf(self.safe)
        after_underlying = underlying.balanceOf(self.safe)

        assert after_etoken > before_etoken
        assert after_underlying < before_underlying

    def deposit_all(self, underlying):
        self.deposit(underlying, underlying.balanceOf(self.safe))

    def withdraw(self, underlying, amount):
        etoken = interface.IEToken(
            self.markets.underlyingToEToken(underlying), owner=self.safe.account
        )

        before_etoken = etoken.balanceOf(self.safe)
        before_underlying = underlying.balanceOf(self.safe)

        etoken.withdraw(0, amount)

        after_etoken = etoken.balanceOf(self.safe)
        after_underlying = underlying.balanceOf(self.safe)

        assert after_etoken < before_etoken
        assert after_underlying > before_underlying + amount

    def withdraw_all(self, underlying):
        self.withdraw(underlying, self.safe.balanceOf(underlying))
