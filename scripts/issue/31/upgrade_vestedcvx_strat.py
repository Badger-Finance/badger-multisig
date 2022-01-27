from eth_abi import encode_abi
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

NEW_LOGIC = registry.eth.logic["native.vestedCVX"] 
DEV_PROXY = registry.eth.badger_wallets.devProxyAdmin

def main(queue="true"):
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
            dump_dir="data/badger/timelock/upgrade_veCVX_strategy/",
            delay_in_days=2.3,
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

        # Execute upgrade
        safe.badger.execute_timelock("data/badger/timelock/upgrade_veCVX_strategy/")

        ## Checking all variables are as expected
        assert prev_strategist == strat_proxy.strategist()
        assert prev_gov == strat_proxy.governance()
        assert prev_guardian == strat_proxy.guardian()
        assert prev_keeper == strat_proxy.keeper()
        assert prev_perFeeG == strat_proxy.performanceFeeGovernance()
        assert prev_perFeeS == strat_proxy.performanceFeeStrategist()
        assert prev_reward == strat_proxy.reward()
        assert prev_unit == strat_proxy.uniswap()

        ## Checking new variables
        assert prev_check_withdrawalSafetyCheck == strat_proxy.withdrawalSafetyCheck()
        assert prev_check_harvestOnRebalance == strat_proxy.harvestOnRebalance()
        assert prev_check_processLocksOnReinvest == strat_proxy.processLocksOnReinvest()
        assert prev_check_processLocksOnRebalance == strat_proxy.processLocksOnRebalance()

        ## Verify new Addresses are setup properly
        assert strat_proxy.LOCKER() == registry.eth.convex.vlCVX
        assert strat_proxy.CVX_EXTRA_REWARDS() == registry.eth.convex.vlCvxExtraRewardDistribution
        assert strat_proxy.VOTIUM_BRIBE_CLAIMER() == registry.eth.votium.multiMerkleStash
        assert strat_proxy.BRIBES_RECEIVER() == registry.eth.badger_wallets.politician_multisig

    safe.post_safe_tx()
