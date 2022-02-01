from brownie import interface
from eth_abi import encode_abi
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from rich.console import Console

C = Console()

TREASURY_OPS = registry.eth.badger_wallets.treasury_ops_multisig
DEV_PROXY = registry.eth.badger_wallets.devProxyAdmin

# Excluding the recovered and mStable controllers purpously
# as their rewards are meant to go to other destinations.
CONTROLLER_IDS = [
    "native",
    "harvest",
    "experimental",
    "bbveCVX-CVX-f",
    "ibBTCCrv",
]


def main(queue="true"):
    """
    Context: As long as the strategist performance fee is set to 0, all performance
    fees go to the controller.rewards() for each strategy's controller. Withdrawal
    fees always go to this address.

    Loops through all controllers and calls setRewards(treasury_ops_multisig) on them.
    Some controllers are governed by the Timelock so this call must be queued.
    Additionally, loops through all strategies and ensures that all of them have their
    performanceFeeStrategist set to 0.
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_badger()

    # Verify that strategist performance fee is 0 for all strats (Except stablecoin strats)
    for key, address in (registry.eth.strategies).items():
        strat = interface.IStrategy(address)
        if strat.performanceFeeStrategist() != 0:
            C.print(f"[red]performanceFeeStrategist not 0 for {key}[red]")

    for controller_id in CONTROLLER_IDS:
        controller = interface.IController(registry.eth.controllers[controller_id])
        if controller.rewards() != TREASURY_OPS:
            if controller.governance() == safe.address:
                controller.setRewards(TREASURY_OPS, {"from": safe.address})
                assert controller.rewards() == TREASURY_OPS
                C.print(f"[green]Rewards set to TreasuryOps on {controller_id}[green]")
            elif controller.governance() == registry.eth.governance_timelock:
                if queue == "true":
                    safe.badger.queue_timelock(
                        target_addr=controller.address,
                        signature="setRewards(address)",
                        data=encode_abi(
                            ["address"],
                            [TREASURY_OPS],
                        ),
                        dump_dir="data/badger/timelock/set_rewards_to_treasury_ops/",
                        delay_in_days=4,
                    )
                    C.print(f"[green]Rewards set to TreasuryOps on {controller_id} was queued![green]")
                else:
                    safe.badger.execute_timelock("data/badger/timelock/set_rewards_to_treasury_ops/")
                    assert controller.rewards() == TREASURY_OPS
                    C.print(f"[green]Rewards set to TreasuryOps on {controller_id}[green]")
            else:
                C.print(
                    f"[red]Governance is not the devMulti nor the Timelock for {controller_id}![red]"
                )
        else:
            C.print(f"[green]Rewards already set to TreasuryOps on {controller_id}[green]")


    safe.post_safe_tx()
    
