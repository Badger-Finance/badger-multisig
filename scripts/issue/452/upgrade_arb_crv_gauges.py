from decimal import Decimal

from brownie import web3, interface, chain
from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import ADDRESSES_ARBITRUM
from helpers.addresses import registry

console = Console()

DEV_MULTI = registry.arbitrum.badger_wallets.dev_multisig
TRICRYPTO_STRATEGY = ADDRESSES_ARBITRUM["strategies"]["native.tricrypto"]
RENCRV_STRATEGY = ADDRESSES_ARBITRUM["strategies"]["native.renCrv"]

TRICRYPTO_GAUGE = "0x555766f3da968ecBefa690Ffd49A2Ac02f47aa5f"
RENCRV_GAUGE = "0xDB3fd1bfC67b5D4325cb31C04E0Cae52f1787FD6"


def main(simulation=True):
    safe = GreatApeSafe(DEV_MULTI)

    console.print(
        f"[green]Setting Tricrypto strategy ({TRICRYPTO_STRATEGY}) gauge to {TRICRYPTO_GAUGE}[/green]"
    )
    set_gauge_and_check_strat(
        TRICRYPTO_STRATEGY, TRICRYPTO_GAUGE, safe, simulation=simulation
    )

    console.print(
        f"[green]Setting Rencrv strategy ({RENCRV_STRATEGY}) gauge to {RENCRV_GAUGE}[/green]"
    )
    set_gauge_and_check_strat(
        RENCRV_STRATEGY, RENCRV_GAUGE, safe, simulation=simulation
    )

    safe.post_safe_tx(call_trace=True)


def set_gauge_and_check_strat(
    strategy_address: str,
    gauge_address: str,
    safe: GreatApeSafe,
    simulation: bool = True,
):
    strategy = interface.ICrvStrategy(strategy_address, owner=safe.account)

    prev_gauge = strategy.gauge()
    prev_balance = strategy.balanceOfPool()

    prev_gauge_contract = interface.ICurveGauge(prev_gauge)
    new_gauge_contract = interface.ICurveGauge(gauge_address)

    strategy.setGauge(gauge_address)

    assert prev_gauge != strategy.gauge()
    assert gauge_address == strategy.gauge()
    assert prev_balance == strategy.balanceOfPool()
    assert prev_balance == new_gauge_contract.balanceOf(strategy_address)
    assert 0 == prev_gauge_contract.balanceOf(strategy_address)

    if simulation:
        chain.mine(72)
        strategy.harvest()
        bal_after_harvest = strategy.balanceOfPool()
        # Appears the gauges aren't distributing rewards yet so this will fail
        # assert bal_after_harvest > prev_balance
