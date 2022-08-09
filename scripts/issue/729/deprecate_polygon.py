from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

TECH_OPS = registry.poly.badger_wallets.techops_multisig

REGISTRY = registry.poly.registry_v2

WBTC_IBBTC_SLP = registry.poly.sett_vaults.bslpibBTCWbtc
WBTC_USDC_QLP = registry.poly.sett_vaults.bqlpUsdcWbtc
AWBTC_REN_CRV = registry.poly.sett_vaults.bcrvRenBTC

def deprecate_polygon():
    safe = GreatApeSafe(TECH_OPS)
    safe.init_badger()

    registry = safe.contract(REGISTRY)

    safe.badger.demote_vault(WBTC_IBBTC_SLP, 0)
    safe.badger.demote_vault(WBTC_USDC_QLP, 0)
    safe.badger.demote_vault(AWBTC_REN_CRV, 0)

    info = registry.productionVaultInfoByVault(WBTC_IBBTC_SLP)
    assert info[2] == 0
    info = registry.productionVaultInfoByVault(WBTC_USDC_QLP)
    assert info[2] == 0
    info = registry.productionVaultInfoByVault(AWBTC_REN_CRV)
    assert info[2] == 0

    safe.post_safe_tx()

