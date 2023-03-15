from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import interface

from rich.console import Console


console = Console()


def main():
    dev = GreatApeSafe(r.badger_wallets.dev_multisig)

    gov_timelock = r.governance_timelock
    registry = dev.contract(r.registry_v2, interface.IBadgerRegistryV2)

    vaults_1_5 = list(registry.getFilteredProductionVaults("v1.5", 3))
    vaults_1_5 = [dev.contract(x[0]) for x in vaults_1_5]

    for vault in vaults_1_5:
        console.print(f"{vault.name()} gov: {vault.governance()}")
        vault.setGovernance(gov_timelock)
        assert vault.governance() == gov_timelock

    dev.post_safe_tx()
