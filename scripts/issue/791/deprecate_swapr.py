from great_ape_safe import GreatApeSafe
from helpers.addresses import registry, get_registry

REGISTRY = get_registry()
TECH_OPS = REGISTRY.badger_wallets.techops_multisig

SWAPR_WETH = REGISTRY.sett_vaults.bdxsSwaprWeth
WBTC_WETH = REGISTRY.sett_vaults.bdxsWbtcWeth
BADGER_WETH = REGISTRY.sett_vaults.bdxsBadgerWeth
IBBTC_WETH = REGISTRY.sett_vaults.bdxsIbbtcWeth


def main():
    safe = GreatApeSafe(TECH_OPS)
    safe.init_badger()

    registry = safe.contract(REGISTRY.registry_v2)

    safe.badger.demote_vault(SWAPR_WETH, 0)
    safe.badger.demote_vault(WBTC_WETH, 0)
    safe.badger.demote_vault(BADGER_WETH, 0)
    safe.badger.demote_vault(IBBTC_WETH, 0)

    info = registry.productionVaultInfoByVault(SWAPR_WETH)
    assert info[2] == 0
    info = registry.productionVaultInfoByVault(WBTC_WETH)
    assert info[2] == 0
    info = registry.productionVaultInfoByVault(BADGER_WETH)
    assert info[2] == 0
    info = registry.productionVaultInfoByVault(IBBTC_WETH)
    assert info[2] == 0

    safe.post_safe_tx()
