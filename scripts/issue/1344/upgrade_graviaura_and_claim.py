from eth_abi import encode_abi
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import accounts, interface
from rich.console import Console
import os
import json

C = Console()

# Contracts
STRAT_PROXY = registry.eth.strategies["native.graviAURA"]
NEW_LOGIC = registry.eth.logic["native.graviAURA"]  # TODO: Under review

# Actors
DEV_PROXY = registry.eth.badger_wallets.devProxyAdmin
TROPS = registry.eth.badger_wallets.treasury_ops_multisig
TECH_OPS = registry.eth.badger_wallets.techops_multisig
DEV = registry.eth.badger_wallets.dev_multisig

# File data
DUMP_DIR = "data/badger/hh_upgrade_claim/"
FILENAME = "bribes_claim_data"

# Tokens
BRIBE_TOKENS = registry.eth.bribe_tokens_claimable_graviaura.values()

# STEP 1: Upgrade and claim bribes into processor


def upgrade_and_claim(queue="true", simulation="false"):
    safe = GreatApeSafe(DEV)
    safe.init_badger()

    strat_proxy = interface.IVestedAura(STRAT_PROXY, owner=safe.account)

    if queue == "true":
        safe.badger.queue_timelock(
            target_addr=DEV_PROXY,
            signature="upgrade(address,address)",
            data=encode_abi(
                ["address", "address"],
                [strat_proxy.address, NEW_LOGIC],
            ),
            dump_dir="data/badger/timelock/upgrade_graviAURA_strategy_V1_1/",
            delay_in_days=4,
        )
    else:
        # Setting all variables, we'll use them later
        prev_want = strat_proxy.want()
        prev_vault = strat_proxy.vault()
        prev_withdrawalMaxDeviationThreshold = (
            strat_proxy.withdrawalMaxDeviationThreshold()
        )
        prev_autoCompoundRatio = strat_proxy.autoCompoundRatio()
        prev_withdrawalSafetyCheck = strat_proxy.withdrawalSafetyCheck()
        prev_processLocksOnReinvest = strat_proxy.processLocksOnReinvest()
        prev_bribesProcessor = strat_proxy.bribesProcessor()
        assert strat_proxy.version() == "1.2"

        # Execute upgrade
        if simulation == "true":
            C.print("Simulating upgrade...")
            timelock = accounts.at(registry.eth.governance_timelock, force=True)
            proxyAdmin = interface.IProxyAdmin(DEV_PROXY, owner=timelock)
            proxyAdmin.upgrade(strat_proxy.address, NEW_LOGIC)
        else:
            # TODO: Add setAuraBalToBalEthBptMinOutBps(9500) on a TechOps script
            safe.badger.execute_timelock(
                "data/badger/timelock/upgrade_graviAURA_strategy_V1_3/"
            )

        ## Checking all variables are as expected
        assert prev_want == strat_proxy.want()
        assert prev_vault == strat_proxy.vault()
        assert (
            prev_withdrawalMaxDeviationThreshold
            == strat_proxy.withdrawalMaxDeviationThreshold()
        )
        assert prev_autoCompoundRatio == strat_proxy.autoCompoundRatio()
        assert prev_withdrawalSafetyCheck == strat_proxy.withdrawalSafetyCheck()
        assert prev_processLocksOnReinvest == strat_proxy.processLocksOnReinvest()
        assert prev_bribesProcessor == strat_proxy.bribesProcessor()
        assert strat_proxy.auraBalToBalEthBptMinOutBps() == 0
        assert strat_proxy.version() == "1.3"

        ## == Post Upgrade actions == ##

        processor = GreatApeSafe(registry.eth.aura_bribes_processor)
        processor.take_snapshot(BRIBE_TOKENS)

        ## Claim accumulated Bribes
        claimed = safe.badger.claim_bribes_hidden_hands()
        print(claimed)
        # dump claim details to file for transfers references
        C.print(f"Dump Directory: {DUMP_DIR}")
        os.makedirs(DUMP_DIR, exist_ok=True)
        with open(f"{DUMP_DIR}{FILENAME}.json", "w") as f:
            json.dump(claimed, f, indent=4, sort_keys=True)

        ## Unfortunately, processor.rageQuit() is only calleable from the manager (TechOps)

        processor.print_snapshot()

    safe.post_safe_tx(post=(simulation != "true"))


# STEP 2: Run script/badger/process_bribes_graviaura.py::ragequit() from TechOps to transfer bribes to DevMultig

# STEP 3: Transfer the amounts received of all bribes from DevMultisig to Trops
def transfer_bribes_to_trops():
    safe = GreatApeSafe(DEV)
    trops = GreatApeSafe(TROPS)
    safe.take_snapshot(BRIBE_TOKENS)
    trops.take_snapshot(BRIBE_TOKENS)

    with open(f"{DUMP_DIR}{FILENAME}.json", "r") as f:
        data = json.load(f)

    for token_address in BRIBE_TOKENS:
        amount = data.get(token_address)
        if amount is not None:
            token = safe.contract(token_address)
            token.transfer(TROPS, amount)

    safe.take_snapshot()
    trops.print_snapshot()
    safe.post_safe_tx()
