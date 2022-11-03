from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

VESTED_AURA = registry.eth.strategies["native.graviAURA"]
GRAVI_AURA = registry.eth.sett_vaults.graviAURA
KEEPER_ACL = registry.eth.keeperAccessControl
DEV_MULTI = registry.eth.badger_wallets.dev_multisig


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    graviAura_strat = interface.IVestedAura(VESTED_AURA, owner=safe.account)
    graviAura_vault = interface.ITheVault(GRAVI_AURA, owner=safe.account)

    # Strategy must be upgraded before delegation
    if graviAura_strat.version() != "1.1":
        return

    # Set slippage protection to 95%
    graviAura_strat.setAuraBalToBalEthBptMinOutBps(9500)
    assert graviAura_strat.auraBalToBalEthBptMinOutBps() == 9500

    # Set keeper back to the Keeper ACL
    graviAura_vault.setKeeper(KEEPER_ACL)
    assert graviAura_vault.keeper() == KEEPER_ACL
    assert graviAura_strat.keeper() == KEEPER_ACL

    # Delegate governance to devMultisig
    graviAura_vault.setGovernance(DEV_MULTI)
    assert graviAura_vault.governance() == DEV_MULTI
    assert graviAura_strat.governance() == DEV_MULTI

    safe.post_safe_tx()
