from brownie import interface
from rich.console import Console
from helpers.addresses import r


C = Console()


class Euler:
    def __init__(self, safe):
        self.safe = safe
        self.euler_markets = interface.IEuler("0x27182842E098f60e3D576794A5bFFb0777E025d3")


    def deposit(self, underlying, amount):
        etoken = self.safe.contract(self.euler_markets.underlyingToEToken(underlying))
        before = etoken.balanceOf(self.safe)
        etoken.deposit(0, amount)
        after = etoken.balanceOf(self.safe)
        assert after > before


    def withdraw():
        pass