import json
import os
import web3

from brownie import accounts, Contract, interface, web3
from eth_abi import encode_abi
from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import ADDRESSES_ETH


console = Console()

# Get addresses
DEV_PROXY = ADDRESSES_ETH["badger_wallets"]["devProxyAdmin"]
DEV_MULTI = ADDRESSES_ETH["badger_wallets"]["dev_multisig"]
TECH_OPS = ADDRESSES_ETH["badger_wallets"]["techops_multisig"]

# Set up safe
safe = GreatApeSafe(DEV_MULTI)
safe.init_badger()

RECOVERED_MULTI = ADDRESSES_ETH["badger_wallets"]["recovered_multisig"]
logic_contracts = ADDRESSES_ETH["logic"]
vaults = ADDRESSES_ETH["sett_vaults"]
vaults.update(ADDRESSES_ETH["yearn_vaults"])

dev_proxy = safe.contract(DEV_PROXY)

# Logic Contracts
SETT_V1H_LOGIC = logic_contracts["SettV1h"]
SETT_V1_1H_LOGIC = logic_contracts["SettV1_1h"]
OLD_V4H_LOGIC = "0x0B7Cb84bc7ad4aF3E1C5312987B6E9A4612068AD"
OLD_V1_1H_LOGIC = "0x25c9BD2eE36ef38992f8a6BE4CadDA9442Bf4170"
SETT_V4H_LOGIC = logic_contracts["SettV4h"]

SETTV1_KEYS = [
    "bBADGER",
    "bcrvRenBTC",
    "bcrvSBTC",
    "bcrvTBTC",
    "bharvestcrvRenBTC",
    "buniWbtcBadger",
]

SETTV1_1_KEYS = [
    "bslpWbtcBadger",
    "bslpWbtcibBTC",
    "buniWbtcDigg",
    "bslpWbtcDigg",
    "bslpWbtcEth",
]

SETTV4_KEYS = [
    "bcrvHBTC",
    "bcrvPBTC",
    "bcrvOBTC",
    "bcrvBBTC",
    "bcrvIbBTC",
    "bcrvTricrypto2",
    "bcvxCRV",
    "bCVX",
    "bveCVX",
    "bimBTC",
    "bFpMbtcHbtc",
    "bbveCVX-CVX-f",
    "bcrvBadger",
]

ACTIVE_V1_1_KEYS = [
    "bslpWbtcBadger",
    "bslpWbtcDigg",
]

ACTIVE_V4_KEYS = [
    "bveCVX",
    "bcrvIbBTC",
    "bcrvBadger",
    "bbveCVX-CVX-f",
    "bcvxCRV",
    "bcrvTricrypto2",
]

SPECIAL_SETTS = [
    "bDIGG",
    "byvWBTC",
    "remBADGER",
    "remDIGG",
]

UPGRADE_SIG = "upgrade(address,address)"
SET_STRATEGIST_SIG = "setStrategist(address)"


def main(queue="true", simulation="false"):
    if queue == "true":
        for key, address in vaults.items():
            address = web3.toChecksumAddress(address)
            if key in SETTV1_KEYS:
                if get_implementation(address) != SETT_V1H_LOGIC:
                    console.print(
                        f"[green]Queueing upgrade on timelock for {key} to SettV1h.sol[/green]"
                    )
                    safe.badger.queue_timelock(
                        target_addr=DEV_PROXY,
                        signature=UPGRADE_SIG,
                        data=encode_abi(
                            ["address", "address"],
                            [address, SETT_V1H_LOGIC],
                        ),
                        dump_dir="data/badger/timelock/upgrade_remaining_setts/",
                        delay_in_days=4,
                    )
                else:
                    console.print(f"[green]{key} has already been upgraded[/green]")

            elif key in SETTV1_1_KEYS:
                if (
                    get_implementation(address) != OLD_V1_1H_LOGIC
                    or key in ACTIVE_V1_1_KEYS
                ):
                    console.print(
                        f"[green]Queueing upgrade on timelock for {key} to SettV1_1h.sol[/green]"
                    )
                    safe.badger.queue_timelock(
                        target_addr=DEV_PROXY,
                        signature=UPGRADE_SIG,
                        data=encode_abi(
                            ["address", "address"],
                            [address, SETT_V1_1H_LOGIC],
                        ),
                        dump_dir="data/badger/timelock/upgrade_remaining_setts/",
                        delay_in_days=4,
                    )
                else:
                    console.print(f"[green]{key} has already been upgraded[/green]")

            elif key in SETTV4_KEYS:
                if (
                    get_implementation(address) != OLD_V4H_LOGIC
                    or key in ACTIVE_V4_KEYS
                ):
                    console.print(
                        f"[green]Queueing upgrade on timelock for {key} to SettV4h.sol[/green]"
                    )
                    safe.badger.queue_timelock(
                        target_addr=DEV_PROXY,
                        signature=UPGRADE_SIG,
                        data=encode_abi(
                            ["address", "address"],
                            [address, SETT_V4H_LOGIC],
                        ),
                        dump_dir="data/badger/timelock/upgrade_remaining_setts/",
                        delay_in_days=4,
                    )
                else:
                    console.print(f"[green]{key} has already been upgraded[/green]")

            elif key in SPECIAL_SETTS:
                console.print(f"[red]No new logic deployed for {key} yet[/red]")

            else:
                console.print(f"[red]{key} is not categorized![/red]")

        safe.post_safe_tx()

    else:
        for key in SETTV1_KEYS + SETTV1_1_KEYS + SETTV4_KEYS:
            execute_timelock(
                safe.badger.timelock,
                "data/badger/timelock/upgrade_remaining_setts/",
                key,
                simulation,
            )

        # Executing all upgrades together
        safe.post_safe_tx()


def execute_timelock(timelock, queueTx_dir, key, simulation):

    if simulation == "false":
        console.print(f"Processing upgrade and patch for {key}...")
        path = os.path.dirname(queueTx_dir)
        directory = os.fsencode(path)

        sett = interface.ISettV4h(vaults[key])

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if not filename.endswith(".json"):
                continue
            txHash = filename.replace(".json", "")

            with open(f"{queueTx_dir}{filename}") as f:
                tx = json.load(f)

            # Get Sett address from upgrade Tx
            target_sett = web3.toChecksumAddress("0x" + tx["data"][24:64])

            if sett.address == target_sett:
                if timelock.queuedTransactions(txHash) == True:

                    # Grab all variables before upgrade
                    prev_available = sett.available()
                    prev_gov = sett.governance()
                    prev_keeper = sett.keeper()
                    prev_token = sett.token()
                    prev_controller = sett.controller()
                    prev_balance = sett.balance()
                    prev_min = sett.min()
                    prev_max = sett.max()
                    prev_getPricePerFullShare = sett.getPricePerFullShare()
                    prev_strategist = sett.strategist()

                    # Executing upgrade
                    console.print(f"[green]Executing tx with parameters:[/green] {tx}")
                    timelock.executeTransaction(
                        tx["target"], 0, tx["signature"], tx["data"], tx["eta"]
                    )

                    # Checking all variables are as expected
                    assert prev_available == sett.available()
                    assert prev_gov == sett.governance()
                    assert prev_keeper == sett.keeper()
                    assert prev_token == sett.token()
                    assert prev_controller == sett.controller()
                    assert prev_balance == sett.balance()
                    assert prev_min == sett.min()
                    assert prev_max == sett.max()
                    assert prev_getPricePerFullShare == sett.getPricePerFullShare()

                    if key in SETTV1_1_KEYS + SETTV4_KEYS:
                        sett.setStrategist(TECH_OPS, {"from": safe.account})
                        assert TECH_OPS == sett.strategist()
                    else:
                        assert prev_strategist == sett.strategist()

                    # Verify new Addresses are setup properly
                    assert sett.MULTISIG() == RECOVERED_MULTI

                else:
                    with open(f"{queueTx_dir}{filename}") as f:
                        tx = json.load(f)
                    console.print(f"[red]Tx not yet queued:[/red] {tx}")

    # Simulate the upgrade execution (And patch balances while we are at it)
    else:
        console.print(f"Running upgrade and patch simulation for {key}...")
        sett = interface.ISettV4h(vaults[key])

        dev_proxy = Contract.from_explorer(DEV_PROXY)
        timelock_actor = accounts.at(ADDRESSES_ETH["governance_timelock"], force=True)

        # Grab all variables before upgrade
        prev_available = sett.available()
        prev_gov = sett.governance()
        prev_keeper = sett.keeper()
        prev_token = sett.token()
        prev_controller = sett.controller()
        prev_balance = sett.balance()
        prev_min = sett.min()
        prev_max = sett.max()
        prev_getPricePerFullShare = sett.getPricePerFullShare()
        prev_available = sett.available()
        prev_strategist = sett.strategist()

        # Execute upgrade
        if key in SETTV1_KEYS:
            dev_proxy.upgrade(sett.address, SETT_V1H_LOGIC, {"from": timelock_actor})
        elif key in SETTV1_1_KEYS:
            dev_proxy.upgrade(sett.address, SETT_V1_1H_LOGIC, {"from": timelock_actor})
            sett.setStrategist(TECH_OPS, {"from": safe.account})
        elif key in SETTV4_KEYS:
            dev_proxy.upgrade(sett.address, SETT_V4H_LOGIC, {"from": timelock_actor})
            sett.setStrategist(TECH_OPS, {"from": safe.account})

        # Checking all variables are as expected
        assert prev_available == sett.available()
        assert prev_gov == sett.governance()
        assert prev_keeper == sett.keeper()
        assert prev_token == sett.token()
        assert prev_controller == sett.controller()
        assert prev_balance == sett.balance()
        assert prev_min == sett.min()
        assert prev_max == sett.max()
        assert prev_getPricePerFullShare == sett.getPricePerFullShare()
        assert prev_available == sett.available()

        if key in SETTV1_1_KEYS + SETTV4_KEYS:
            assert TECH_OPS == sett.strategist()
            # test can call approve and revoke from tech ops
            sett.approveContractAccess(accounts[0], {"from": TECH_OPS})
            sett.revokeContractAccess(accounts[0], {"from": TECH_OPS})
        else:
            assert prev_strategist == sett.strategist()

        # Verify new Addresses are setup properly
        assert sett.MULTISIG() == RECOVERED_MULTI

        console.print(f"[green]Simulation successful for {key}[/green]")


def get_implementation(proxy):
    IMPLEMENTATION_SLOT = (
        "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
    )
    return web3.toChecksumAddress(
        web3.eth.getStorageAt(proxy, IMPLEMENTATION_SLOT).hex()
    )
