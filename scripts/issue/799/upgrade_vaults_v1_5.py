from eth_abi import encode_abi
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import accounts, interface, web3
from rich.console import Console
import json
import os

C = Console()

VAULTS = registry.eth.sett_vaults
NEW_LOGIC = registry.eth.logic.TheVault
DEV_PROXY = registry.eth.badger_wallets.devProxyAdmin

KEYS = [
    "graviAURA",
    "bauraBal",
    "b80BADGER_20WBTC",
    "b40WBTC_40DIGG_20graviAURA",
    "bBB_a_USD",
    "b33auraBAL_33graviAURA_33WETH"
]


def main(queue="true", simulation="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_badger()

    for key, address in VAULTS.items():
        address = web3.toChecksumAddress(address)
        print(key)
        print(address)
        if key in KEYS:
            if queue == "true":
                C.print(f"[green]Queuing upgrade for {key}[/green]")
                safe.badger.queue_timelock(
                    target_addr=DEV_PROXY,
                    signature="upgrade(address,address)",
                    data=encode_abi(
                        ["address", "address"],
                        [address, NEW_LOGIC],
                    ),
                    dump_dir="data/badger/timelock/upgrade_vaults_v1_5_fee_events/",
                    delay_in_days=4,
                )
            else:
                execute_timelock(
                    safe.badger.timelock,
                    "data/badger/timelock/upgrade_vaults_v1_5_fee_events/",
                    key,
                    address,
                    simulation,
                    safe
                )
        
    safe.post_safe_tx()


def execute_timelock(timelock, queueTx_dir, key, address, simulation, safe):
    vault = interface.ITheVault(address)
    if simulation == "false":
        path = os.path.dirname(queueTx_dir)
        directory = os.fsencode(path)

        C.print(f"[green]Executing upgrade for {key}[/green]")

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if not filename.endswith(".json"):
                continue
            txHash = filename.replace(".json", "")

            with open(f"{queueTx_dir}{filename}") as f:
                tx = json.load(f)

            # Get vault address from upgrade Tx
            target_vault = web3.toChecksumAddress("0x" + tx["data"][24:64])

            if vault.address == target_vault:
                if timelock.queuedTransactions(txHash) == True:

                    # Grab all variables before upgrade
                    prev_available = vault.available()
                    prev_gov = vault.governance()
                    prev_keeper = vault.keeper()
                    prev_guardian = vault.guardian()
                    prev_strategist = vault.strategist()
                    prev_treasury = vault.treasury()
                    prev_token = vault.token()
                    prev_symbol = vault.symbol()
                    prev_balance = vault.balance()
                    prev_totalSupply = vault.totalSupply()
                    prev_getPricePerFullShare = vault.getPricePerFullShare()

                    # Executing upgrade
                    C.print(f"[green]Executing tx with parameters:[/green] {tx}")
                    timelock.executeTransaction(
                        tx["target"], 0, tx["signature"], tx["data"], tx["eta"]
                    )

                    # Checking all variables are as expected
                    assert prev_available == vault.available()
                    assert prev_gov == vault.governance()
                    assert prev_keeper == vault.keeper()
                    assert prev_guardian == vault.guardian()
                    assert prev_strategist == vault.strategist()
                    assert prev_treasury == vault.treasury()
                    assert prev_token == vault.token()
                    assert prev_symbol == vault.symbol()
                    assert prev_balance == vault.balance()
                    assert prev_totalSupply == vault.totalSupply()
                    assert prev_getPricePerFullShare == vault.getPricePerFullShare()

                else:
                    with open(f"{queueTx_dir}{filename}") as f:
                        tx = json.load(f)
                    C.print(f"[red]Tx not yet queued:[/red] {tx}")

    # Simulate the upgrade execution and ensure that fee events get emitted properly
    else:
        C.print(f"[green]Running upgrade simulation for {key}...")

        dev_proxy = interface.IProxyAdmin(DEV_PROXY)
        timelock_actor = accounts.at(safe.badger.timelock.address, force=True)

        # Grab all variables before upgrade
        prev_available = vault.available()
        prev_gov = vault.governance()
        prev_keeper = vault.keeper()
        prev_guardian = vault.guardian()
        prev_strategist = vault.strategist()
        prev_treasury = vault.treasury()
        prev_token = vault.token()
        prev_symbol = vault.symbol()
        prev_balance = vault.balance()
        prev_totalSupply = vault.totalSupply()
        prev_getPricePerFullShare = vault.getPricePerFullShare()

        # Execute upgrade
        dev_proxy.upgrade(vault.address, NEW_LOGIC, {"from": timelock_actor})

        # Checking all variables are as expected
        assert prev_available == vault.available()
        assert prev_gov == vault.governance()
        assert prev_keeper == vault.keeper()
        assert prev_guardian == vault.guardian()
        assert prev_strategist == vault.strategist()
        assert prev_treasury == vault.treasury()
        assert prev_token == vault.token()
        assert prev_symbol == vault.symbol()
        assert prev_balance == vault.balance()
        assert prev_totalSupply == vault.totalSupply()
        assert prev_getPricePerFullShare == vault.getPricePerFullShare()

        strat = interface.IStrategy(vault.strategy())
        tx = strat.harvest({"from": safe.account})
        # New event triggers
        assert len(tx.events["PerformanceFeeGovernance"]) >= 1

        C.print(f"[green]Simulation successful for {key}[/green]")
