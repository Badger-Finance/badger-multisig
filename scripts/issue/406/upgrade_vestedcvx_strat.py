from eth_abi import encode_abi
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import accounts, interface, chain
from helpers.constants import EmptyBytes32
from rich.console import Console

C = Console()

NEW_LOGIC = registry.eth.logic["native.vestedCVX"] 
DEV_PROXY = registry.eth.badger_wallets.devProxyAdmin


def main(queue="true", simulation="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_badger()

    strat_proxy = safe.badger.strat_bvecvx

    if queue == "true":
        safe.badger.queue_timelock(
            target_addr=DEV_PROXY,
            signature="upgrade(address,address)",
            data=encode_abi(
                ["address", "address"],
                [strat_proxy.address, NEW_LOGIC],
            ),
            dump_dir="data/badger/timelock/upgrade_veCVX_strategy_V1_6/",
            delay_in_days=4,
        )
    else:   
        # Setting all variables, we'll use them later
        prev_strategist = strat_proxy.strategist()
        prev_gov = strat_proxy.governance()
        prev_guardian = strat_proxy.guardian()
        prev_keeper = strat_proxy.keeper()
        prev_perFeeG = strat_proxy.performanceFeeGovernance()
        prev_perFeeS = strat_proxy.performanceFeeStrategist()
        prev_reward = strat_proxy.reward()
        prev_unit = strat_proxy.uniswap()
        prev_check_withdrawalSafetyCheck = strat_proxy.withdrawalSafetyCheck()
        prev_check_harvestOnRebalance = strat_proxy.harvestOnRebalance()
        prev_check_processLocksOnReinvest = strat_proxy.processLocksOnReinvest()
        prev_check_processLocksOnRebalance = strat_proxy.processLocksOnRebalance()

        # Constants
        prev_CVX_EXTRA_SNAPSHOT = strat_proxy.SNAPSHOT()
        prev_CVX_EXTRA_BADGER_TREE = strat_proxy.BADGER_TREE()
        prev_DELEGATE = strat_proxy.DELEGATE()
        prev_DELEGATED_SPACE = strat_proxy.DELEGATED_SPACE()
        prev_CVXCRV_VAULT = strat_proxy.CVXCRV_VAULT()
        prev_LOCKER = strat_proxy.LOCKER()
        prev_CVX_EXTRA_REWARDS = strat_proxy.CVX_EXTRA_REWARDS()
        prev_CVX_VOTIUM_BRIBE_CLAIMER = strat_proxy.VOTIUM_BRIBE_CLAIMER()
        prev_CVX_EXTRA_BADGER = strat_proxy.BADGER()

        # Execute upgrade
        if simulation == "true":
            C.print("Simulating upgrade...")
            timelock = accounts.at(registry.eth.governance_timelock, force=True)
            proxyAdmin = interface.IProxyAdmin(DEV_PROXY, owner=timelock)
            proxyAdmin.upgrade(strat_proxy.address, NEW_LOGIC)
        else:
            safe.badger.execute_timelock("data/badger/timelock/upgrade_veCVX_strategy_V1_6/")

        ## Checking all variables are as expected
        assert prev_strategist == strat_proxy.strategist()
        assert prev_gov == strat_proxy.governance()
        assert prev_guardian == strat_proxy.guardian()
        assert prev_keeper == strat_proxy.keeper()
        assert prev_perFeeG == strat_proxy.performanceFeeGovernance()
        assert prev_perFeeS == strat_proxy.performanceFeeStrategist()
        assert prev_reward == strat_proxy.reward()
        assert prev_unit == strat_proxy.uniswap()
        assert prev_check_withdrawalSafetyCheck == strat_proxy.withdrawalSafetyCheck()
        assert prev_check_harvestOnRebalance == strat_proxy.harvestOnRebalance()
        assert prev_check_processLocksOnReinvest == strat_proxy.processLocksOnReinvest()
        assert prev_check_processLocksOnRebalance == strat_proxy.processLocksOnRebalance()

        # Verify constants
        assert prev_CVX_EXTRA_SNAPSHOT == strat_proxy.SNAPSHOT()
        assert prev_CVX_EXTRA_BADGER_TREE == strat_proxy.BADGER_TREE()
        assert prev_DELEGATE == strat_proxy.DELEGATE()
        assert prev_DELEGATED_SPACE == strat_proxy.DELEGATED_SPACE()
        assert prev_CVXCRV_VAULT == strat_proxy.CVXCRV_VAULT()
        assert prev_LOCKER == strat_proxy.LOCKER()
        assert prev_CVX_EXTRA_REWARDS == strat_proxy.CVX_EXTRA_REWARDS()
        assert prev_CVX_VOTIUM_BRIBE_CLAIMER == strat_proxy.VOTIUM_BRIBE_CLAIMER()
        assert prev_CVX_EXTRA_BADGER == strat_proxy.BADGER()

        ## Verify new Addresses are setup properly
        assert strat_proxy.BRIBES_PROCESSOR() == registry.eth.bribes_processor

        # Test chainlink functions
        if simulation == "true":
            C.print("[green]Simulation Successful![/green]")

    safe.post_safe_tx(post=(simulation!="true"))
