from eth_abi import encode_abi
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import accounts, interface
from rich.console import Console

C = Console()

STRAT_PROXY = registry.eth.strategies["native.graviAURA"] 
NEW_LOGIC = registry.eth.logic["native.graviAURA"] 
DEV_PROXY = registry.eth.badger_wallets.devProxyAdmin
TECH_OPS = registry.eth.badger_wallets.techops_multisig


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
            dump_dir="data/badger/timelock/upgrade_graviAURA_strategy_V1_1/",
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
        assert strat_proxy.version() == "1.0"

        # Execute upgrade
        if simulation == "true":
            C.print("Simulating upgrade...")
            timelock = accounts.at(registry.eth.governance_timelock, force=True)
            proxyAdmin = interface.IProxyAdmin(DEV_PROXY, owner=timelock)
            proxyAdmin.upgrade(strat_proxy.address, NEW_LOGIC)
        else:
            # TODO: Add setAuraBalToBalEthBptMinOutBps(9500) on a TechOps script
            safe.badger.execute_timelock("data/badger/timelock/upgrade_graviAURA_strategy_V1_1/")

        ## Checking all variables are as expected
        assert prev_want == strat_proxy.want()
        assert prev_vault == strat_proxy.vault()
        assert prev_withdrawalMaxDeviationThreshold == strat_proxy.withdrawalMaxDeviationThreshold()
        assert prev_autoCompoundRatio == strat_proxy.autoCompoundRatio()
        assert prev_withdrawalSafetyCheck == strat_proxy.withdrawalSafetyCheck()
        assert prev_processLocksOnReinvest == strat_proxy.processLocksOnReinvest()
        assert prev_bribesProcessor == strat_proxy.bribesProcessor()
        assert strat_proxy.auraBalToBalEthBptMinOutBps() == 0
        assert strat_proxy.version() == "1.1"

        if simulation == "true":
            techOps = accounts.at(TECH_OPS, force=True)
            ## Set slippage tolerance to 95% (TechOps is currently governance/strategist)
            strat_proxy.setAuraBalToBalEthBptMinOutBps(9500, {"from": techOps})

            ## Test running a harvest
            strat_proxy.harvest({"from": techOps})
            C.print("[green]Simulation Successful![/green]")

    safe.post_safe_tx(post=(simulation!="true"))