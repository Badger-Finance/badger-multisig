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


def main(submitTx="true", queue="true", simulation="true"):

    if queue == "true":
        # Queue txs on Timelock
        for key in KEYS:
            strategy_address = STRATEGIES[key]
            strategy_contract = interface.IStrategy(strategy_address)
            vault_address = VAULTS[key]
            vault_contract = interface.ISettV4h(vault_address)

            console.print(f"Approving strategy and setting vault for {key}")
            safe.badger.queue_timelock(
                target_addr=NATIVE_CONTROLLER,
                signature="approveStrategy(address,address)",
                data=encode_abi(
                    ["address", "address"],
                    [strategy_contract.want(), strategy_address],
                ),
                dump_dir=TX_DIR,
                delay_in_days=6,
            )

            safe.badger.queue_timelock(
                target_addr=NATIVE_CONTROLLER,
                signature="setVault(address,address)",
                data=encode_abi(
                    ["address", "address"],
                    [vault_contract.token(), vault_address],
                ),
                dump_dir=TX_DIR,
                delay_in_days=6,
            )

    if submitTx == "true":
        safe.badger.execute_timelock(TX_DIR)

        native = safe.contract(NATIVE_CONTROLLER)
        for key in KEYS:
            strategy_address = STRATEGIES[key]
            strategy_contract = interface.IStrategy(
                strategy_address, owner=safe.account
            )
            vault_address = VAULTS[key]
            vault_contract = interface.ISettV4h(vault_address, owner=safe.account)

            console.print(f"Setting strategy and controllers for {key}")
            native.setStrategy(strategy_contract.want(), strategy_address)

            strategy_contract.setController(NATIVE_CONTROLLER)
            vault_contract.setController(NATIVE_CONTROLLER)

            assert vault_contract.controller() == NATIVE_CONTROLLER
            assert strategy_contract.controller() == NATIVE_CONTROLLER

            if simulation:
                chain.sleep(86400)
                chain.mine()

                console.print("Trying to harvest")
                strategy_contract.harvest()

                console.print("Trying to earn")
                vault_contract.earn()

    safe.post_safe_tx()
