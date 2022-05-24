from decimal import Decimal

from brownie import accounts, web3, interface, chain
from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import ADDRESSES_ETH
from helpers.addresses import registry

console = Console()

DEV_MULTI = registry.eth.badger_wallets.dev_multisig

PBTC_STRATEGY_DEP = ADDRESSES_ETH["strategies"]["_deprecated"]["native.pbtcCrv"]["v1"]
PBTC_STRATEGY = ADDRESSES_ETH["strategies"]["native.pbtcCrv"]

OBTC_STRATEGY_DEP = ADDRESSES_ETH["strategies"]["_deprecated"]["native.obtcCrv"]["v1"]
OBTC_STRATEGY = ADDRESSES_ETH["strategies"]["native.obtcCrv"]

PNT = ADDRESSES_ETH["treasury_tokens"]["PNT"]
BOR = ADDRESSES_ETH["treasury_tokens"]["BOR"]
BORING = ADDRESSES_ETH["treasury_tokens"]["BORING"]

STRATEGIES = [PBTC_STRATEGY_DEP, PBTC_STRATEGY, OBTC_STRATEGY_DEP, OBTC_STRATEGY]
STRATEGY_MAPPING = {
    PBTC_STRATEGY_DEP: "pbtcCrv_deprecated",
    PBTC_STRATEGY: "pbtcCrv",
    OBTC_STRATEGY_DEP: "obtcCrv_deprecated",
    OBTC_STRATEGY: "obtcCrv",
}

TOKENS = [PNT, BOR, BORING]
TOKEN_MAPPING = {
    PNT: "PNT",
    BOR: "BOR",
    BORING: "BORING",
}


def main(simulation="false"):

    safe = GreatApeSafe(DEV_MULTI)

    for strategy in STRATEGIES:
        console.print(f"[green]Sweeping {STRATEGY_MAPPING[strategy]}[/green]")
        sweep_strategy(strategy, safe, simulation)

    safe.post_safe_tx(call_trace=True)


def sweep_strategy(
    strategy_address: str,
    safe: GreatApeSafe,
    simulation: bool = True,
):
    strategy = interface.IStrategy(strategy_address, owner=safe.account)

    controller_address = strategy.controller()
    controller = interface.IController(controller_address, owner=safe.account)

    for token_address in TOKENS:
        token = interface.IERC20(token_address)

        strategy_balance = token.balanceOf(strategy_address)
        controller_balance = token.balanceOf(controller_address)
        safe_balance_prev = token.balanceOf(safe.address)

        assert 0 == controller_balance

        if strategy_balance > 0:
            console.print(
                f"[green]Sweeping {strategy_balance} {TOKEN_MAPPING[token_address]} from strategy[/green]"
            )
            controller.inCaseStrategyTokenGetStuck(strategy_address, token_address)
            controller_balance += token.balanceOf(controller_address)
            controller.inCaseTokensGetStuck(token_address, controller_balance)
            assert strategy_balance == token.balanceOf(safe.address) - safe_balance_prev
            assert token.balanceOf(safe.address) > safe_balance_prev

        assert 0 == token.balanceOf(strategy_address)
        assert 0 == token.balanceOf(controller_address)
