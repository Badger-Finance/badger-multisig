from brownie import interface, Contract
from rich.console import Console
from brownie.test.managers.runner import RevertContextManager as reverts
from helpers.addresses import registry
from great_ape_safe import GreatApeSafe

C = Console()

STRAT_ADDRESS = registry.ftm.strategies["native.bveOXD-OXD"]
DEV_PROXY = registry.ftm.badger_wallets.devProxyAdmin
DEV_MULTI = registry.ftm.badger_wallets.dev_multisig
NEW_LOGIC = registry.ftm.logic["StrategybveOxdOxdStakingOptimizer"] 

def main(simulation="false"):
    safe = GreatApeSafe(DEV_MULTI)
    strat_contract = Contract(STRAT_ADDRESS)
    strat = interface.IStrategy(STRAT_ADDRESS, owner=safe.account)

    # Record storage variables
    attributes = {}
    for attr in strat_contract.signatures:
        try:
            attributes[attr] = getattr(strat_contract, attr).call()
        except:
            C.print(f"[red]Error storing {attr}[/red]")
            pass

    # Test failing harvest
    if simulation == "true":
        with reverts("BaseV1Router: INSUFFICIENT_B_AMOUNT"):
            strat.harvest({"from": safe.account})

    # Execute upgrade
    proxy_admin = interface.IProxyAdmin(DEV_PROXY, owner=safe.account)
    proxy_admin.upgrade(strat.address, NEW_LOGIC)

    # Confirm storage variables
    for attr in strat_contract.signatures:
        try:
            assert attributes[attr] == getattr(strat_contract, attr).call()
        # Should fail if assertion is wrong
        except KeyError:
            C.print(f"[red]Error confirming {attr}[/red]")
            pass

    # Test harvest
    if simulation == "true":
        strat.harvest({"from": safe.account})

    safe.post_safe_tx(post=(simulation!="true"))