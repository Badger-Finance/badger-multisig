import json
import os
import web3

from brownie import accounts, chain, Contract, interface, web3
from eth_abi import encode_abi
from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import ADDRESSES_ETH, registry


console = Console()

# Get addresses
DEV_MULTI = registry.eth.badger_wallets.dev_multisig
NATIVE_CONTROLLER = registry.eth.controllers.native

KEYS = [
    "bbveCVX-CVX-f",
    "bcrvBadger",
    "bcrvIbBTC",
]

STRATEGIES = {
    "bbveCVX-CVX-f": ADDRESSES_ETH["strategies"]["native.bbveCVX-CVX-f"],
    "bcrvBadger": ADDRESSES_ETH["strategies"]["native.bcrvBadger"],
    "bcrvIbBTC": ADDRESSES_ETH["strategies"]["native.bcrvIbBTC"],
}

VAULTS = {
    "bbveCVX-CVX-f": ADDRESSES_ETH["sett_vaults"]["bbveCVX-CVX-f"],
    "bcrvBadger": ADDRESSES_ETH["sett_vaults"]["bcrvBadger"],
    "bcrvIbBTC": ADDRESSES_ETH["sett_vaults"]["bcrvIbBTC"],
}

# Set up safe
safe = GreatApeSafe(DEV_MULTI)
safe.init_badger()

# Other constants
TX_DIR = "data/badger/timelock/upgrade_new_sett_controllers/"
TIMELOCK_DELAY_DAYS=4


def main(submit_tx="false", queue="true", simulation="false"):

    if queue == "true":
        # Queue txs on Timelock
        for key in KEYS:
            strategy_address = STRATEGIES[key]
            strategy_contract = interface.IStrategy(strategy_address)
            vault_address = VAULTS[key]
            vault_contract = interface.ISettV4h(vault_address)

            console.print(
                f"[green]Approving strategy and setting vault for {key}[/green]"
            )
            safe.badger.queue_timelock(
                target_addr=NATIVE_CONTROLLER,
                signature="approveStrategy(address,address)",
                data=encode_abi(
                    ["address", "address"],
                    [strategy_contract.want(), strategy_address],
                ),
                dump_dir=TX_DIR,
                delay_in_days=TIMELOCK_DELAY_DAYS,
            )

            safe.badger.queue_timelock(
                target_addr=NATIVE_CONTROLLER,
                signature="setVault(address,address)",
                data=encode_abi(
                    ["address", "address"],
                    [vault_contract.token(), vault_address],
                ),
                dump_dir=TX_DIR,
                delay_in_days=TIMELOCK_DELAY_DAYS,
            )

    if submit_tx == "true":
        if simulation != "true":
            safe.badger.execute_timelock(TX_DIR)

        native = safe.contract(NATIVE_CONTROLLER)
        for key in KEYS:
            strategy_address = STRATEGIES[key]
            strategy_contract = interface.IStrategy(
                strategy_address, owner=safe.account
            )
            vault_address = VAULTS[key]
            vault_contract = interface.ISettV4h(vault_address, owner=safe.account)

            console.print(f"[green]Setting strategy and controllers for {key}[/green]")

            if simulation == "true":
                timelock = accounts.at(registry.eth.governance_timelock, force=True)
                controller = interface.IController(NATIVE_CONTROLLER, owner=timelock)
                controller.approveStrategy(strategy_contract.want(), strategy_address)
                controller.setVault(vault_contract.token(), vault_address)

            native.setStrategy(strategy_contract.want(), strategy_address)

            strategy_contract.setController(NATIVE_CONTROLLER)
            vault_contract.setController(NATIVE_CONTROLLER)

            assert vault_contract.controller() == NATIVE_CONTROLLER
            assert strategy_contract.controller() == NATIVE_CONTROLLER

            if simulation == "true":
                chain.sleep(86400)
                chain.mine()

                console.print("Trying to harvest")
                strategy_contract.harvest()

                console.print("Trying to earn")
                vault_contract.earn()

    if simulation != "true":
        safe.post_safe_tx()
