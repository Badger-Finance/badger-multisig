from eth_abi import encode_abi
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import accounts, interface
from rich.console import Console

C = Console()

STRAT_PROXY = registry.eth.strategies["native.graviAURA"] 
NEW_LOGIC = registry.eth.logic["native.graviAURA"] 
DEV_PROXY = registry.eth.badger_wallets.devProxyAdmin
TROPS = registry.eth.badger_wallets.treasury_ops_multisig
BADGER = registry.eth.treasury_tokens.BADGER
TARGET_DELEGATE = registry.eth.badger_wallets.delegate

BALANCER_SPACE_ID = "0x62616c616e6365722e6574680000000000000000000000000000000000000000"


def main(queue="true", simulation="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
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
            dump_dir="data/badger/timelock/upgrade_graviAURA_strategy_V1_2/",
            delay_in_days=4,
        )
    else:   
        # Setting all variables, we'll use them later
        prev_want = strat_proxy.want()
        prev_vault = strat_proxy.vault()
        prev_withdrawalMaxDeviationThreshold = strat_proxy.withdrawalMaxDeviationThreshold()
        prev_autoCompoundRatio = strat_proxy.autoCompoundRatio()
        prev_withdrawalSafetyCheck = strat_proxy.withdrawalSafetyCheck()
        prev_processLocksOnReinvest = strat_proxy.processLocksOnReinvest()
        prev_bribesProcessor = strat_proxy.bribesProcessor()
        prev_auraBalToBalEthBptMinOutBps = strat_proxy.auraBalToBalEthBptMinOutBps()
        prev_balanceOf = strat_proxy.balanceOf()
        prev_balanceOfPool = strat_proxy.balanceOfPool()
        prev_balanceOfWant = strat_proxy.balanceOfWant()
        assert strat_proxy.version() == "1.1"

        # Execute upgrade
        if simulation == "true":
            C.print("Simulating upgrade...")
            timelock = accounts.at(registry.eth.governance_timelock, force=True)
            proxyAdmin = interface.IProxyAdmin(DEV_PROXY, owner=timelock)
            proxyAdmin.upgrade(strat_proxy.address, NEW_LOGIC)
        else:
            safe.badger.execute_timelock("data/badger/timelock/upgrade_graviAURA_strategy_V1_2/")

        ## Checking all variables are as expected
        assert prev_want == strat_proxy.want()
        assert prev_vault == strat_proxy.vault()
        assert prev_withdrawalMaxDeviationThreshold == strat_proxy.withdrawalMaxDeviationThreshold()
        assert prev_autoCompoundRatio == strat_proxy.autoCompoundRatio()
        assert prev_withdrawalSafetyCheck == strat_proxy.withdrawalSafetyCheck()
        assert prev_processLocksOnReinvest == strat_proxy.processLocksOnReinvest()
        assert prev_bribesProcessor == strat_proxy.bribesProcessor()
        assert prev_auraBalToBalEthBptMinOutBps == strat_proxy.auraBalToBalEthBptMinOutBps()
        assert prev_balanceOf == strat_proxy.balanceOf()
        assert prev_balanceOfPool == strat_proxy.balanceOfPool()
        assert prev_balanceOfWant == strat_proxy.balanceOfWant()
        assert strat_proxy.version() == "1.2"
        assert strat_proxy.LOCKER() == "0x3Fa73f1E5d8A792C80F426fc8F84FBF7Ce9bBCAC"

        # Set BADGER redirection path atomically
        # BADGER -> Trops (with 0% fee)
        strat_proxy.setRedirectionToken(BADGER, TROPS, 0)
        assert strat_proxy.bribesRedirectionPaths(BADGER) == TROPS
        assert strat_proxy.redirectionFees(BADGER) == 0

        # Set balancer snapshot delegation
        strat_proxy.setSnapshotDelegate(BALANCER_SPACE_ID, TARGET_DELEGATE)
        assert strat_proxy.getSnapshotDelegate(BALANCER_SPACE_ID) == TARGET_DELEGATE

        if simulation == "true":
            ## Test sweeping a redirected token (BADGER)
            amount = 1000e18
            badger = interface.IERC20(BADGER)
            whale = accounts.at(registry.eth.badger_wallets.treasury_vault_multisig, force=True)
            badger.transfer(strat_proxy, amount, {"from": whale})
            assert badger.balanceOf(strat_proxy) == amount
            previous_trops_balance = badger.balanceOf(TROPS)

            # Sweeps BADGER into its redirection recepient
            strat_proxy.sweepRewardToken(BADGER)

            # Whole balance of strat must have been redirected to destination since fee is 0%
            assert badger.balanceOf(TROPS) == previous_trops_balance + amount
            assert badger.balanceOf(strat_proxy) == 0

            ## Test running a harvest
            strat_proxy.harvest()
            C.print("[green]Simulation Successful![/green]")

        else:
            safe.post_safe_tx()