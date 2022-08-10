from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from rich.console import Console

C = Console()

TECH_OPS = registry.eth.badger_wallets.techops_multisig
DEV = registry.eth.badger_wallets.dev_multisig
REGISTRY = registry.eth.registry_v2
VAULTS = registry.eth.sett_vaults
STATUS = 1 # Guarded
VAULT_IDS = [
    "bauraBal",
    "b80BADGER_20WBTC",
    "b40WBTC_40DIGG_20graviAURA",
    "bBB_a_USD",
    "b33auraBAL_33graviAURA_33WETH"
]

def main():
    safe = GreatApeSafe(TECH_OPS)
    safe.init_badger()

    registry = safe.contract(REGISTRY)

    for id in VAULT_IDS:
        info = registry.productionVaultInfoByVault(VAULTS[id])
        safe.badger.promote_vault(info[0], info[1], info[3], STATUS)
        assert registry.productionVaultInfoByVault(VAULTS[id])[2] == STATUS

    safe.post_safe_tx()