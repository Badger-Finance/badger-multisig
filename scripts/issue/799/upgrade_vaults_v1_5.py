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
    "b33auraBAL_33graviAURA_33WETH",
    "bB_stETH_STABLE",
    "bB-rETH-STABLE"
]

HODLERS = [
    "0xD14f076044414C255D2E82cceB1CB00fb1bBA64c",
    "0xfe51263bd0d075dc5441e89ecd1f6d63ff41e02e",
    "0xec4fcd1aca723f8456999c5f5d7479dbe9528c11",
    "0x95eec544a7cf2e6a65a71039d58823f4564a6319",
    "0xc3b1f7ab9fabd729cdf9e90ea54ec447f9464269",
    "0x794783dcfcac8c1944727057a3208d8f8bb91506",
    "0xee8b29aa52dd5ff2559da2c50b1887adee257556",
    "0xee8b29aa52dd5ff2559da2c50b1887adee257556"
]


def main(queue="true", simulation="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_badger()

    for key, address in VAULTS.items():
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
                    dump_dir="data/badger/timelock/upgrade_vaults_v1_5_2a_fee_events/",
                    delay_in_days=4,
                )
            else:
                execute_timelock(
                    safe.badger.timelock,
                    "data/badger/timelock/upgrade_vaults_v1_5_2a_fee_events/",
                    key,
                    address,
                    simulation,
                    safe
                )
        
    safe.post_safe_tx(replace_nonce=1079)


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

                    # save storage vars
                    attributes = {}
                    for attr in vault.signatures:
                        try:
                            attributes[attr] = getattr(vault, attr).call()
                        except:
                            C.print(f'[red]error storing {attr}[/red]')

                    # Executing upgrade
                    C.print(f"[green]Executing tx with parameters:[/green] {tx}")
                    timelock.executeTransaction(
                        tx["target"], 0, tx["signature"], tx["data"], tx["eta"]
                    )

                    # assert storage vars
                    for attr in vault.signatures:
                        try:
                            assert attributes[attr] == getattr(vault, attr).call()
                            C.print(f'[green]asserted {attr}[/green]')
                        except:
                            pass

                else:
                    with open(f"{queueTx_dir}{filename}") as f:
                        tx = json.load(f)
                    C.print(f"[red]Tx not yet queued:[/red] {tx}")

    # Simulate the upgrade execution and ensure that fee events get emitted properly
    else:
        C.print(f"[green]Running upgrade simulation for {key}...")

        dev_proxy = interface.IProxyAdmin(DEV_PROXY)
        timelock_actor = accounts.at(safe.badger.timelock.address, force=True)

        # save storage vars
        attributes = {}
        for attr in vault.signatures:
            try:
                attributes[attr] = getattr(vault, attr).call()
            except:
                C.print(f'[red]error storing {attr}[/red]')

        # Execute upgrade
        dev_proxy.upgrade(vault.address, NEW_LOGIC, {"from": timelock_actor})

        # assert storage vars
        for attr in vault.signatures:
            try:
                assert attributes[attr] == getattr(vault, attr).call()
                C.print(f'[green]asserted {attr}[/green]')
            except:
                pass

        # Simulate a harvest
        strat = interface.IStrategy(vault.strategy())
        tx = strat.harvest({"from": safe.account})
        # New event triggers
        assert len(tx.events["PerformanceFeeGovernance"]) >= 1

        # Simulate a withdrawal
        if vault.withdrawalFee() > 0:
            hodler = accounts.at(HODLERS[KEYS.index(key)], force=True)
            tx = vault.withdrawAll({"from": hodler})
            # New event triggers
            assert len(tx.events["WithdrawalFee"]) >= 1

        C.print(f"[green]Simulation successful for {key}[/green]")
