from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface

from rich.console import Console

console = Console()

NEW_STRAT_FEE = 0
NEW_GOV_FEE = 2000


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    strategies = registry.eth.strategies

    for key, addr in strategies.items():
        strategy = interface.IStrategy(addr, owner=safe.address)

        if strategy.performanceFeeStrategist() != 0:
            console.print(
                f"[red] === Strategy {key} has perf fee strategist not set to 0, current value {strategy.performanceFeeStrategist()} === [/red]"
            )

            if strategy.governance() == safe.address:
                strategy.setPerformanceFeeStrategist(NEW_STRAT_FEE)
                assert strategy.performanceFeeStrategist() == NEW_STRAT_FEE
                console.print(
                    f"[green] === Succesfully set 0 perf strategist in {key} === \n[/green]"
                )

                # change also perf gov fee
                if strategy.performanceFeeGovernance() != 2000:
                    console.print(
                        f"[red] === Strategy {key} has perf fee gov different than 2000, current value {strategy.performanceFeeGovernance()} === [/red]"
                    )
                    strategy.setPerformanceFeeGovernance(NEW_GOV_FEE)
                    assert strategy.performanceFeeGovernance() == NEW_GOV_FEE
                    console.print(
                        f"[green] === Succesfully set 2000 perf gov in {key} === \n[/green]"
                    )

    safe.post_safe_tx()