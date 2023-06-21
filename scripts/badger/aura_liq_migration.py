from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# New pids
AURA_NEW_PID_WBTC_BADGER = 111  # https://app.aura.finance/#/pool/111
AURA_NEW_PID_WBTC_DIGG_GRAVI = 112  # https://app.aura.finance/#/pool/112


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    migrator = vault.contract(r.aura.gauge_migrator)
    aura_20wbtc80badger = vault.contract(r.aura.aura_20wbtc80badger_gauge)
    aura_20wbtc80badger_old = vault.contract(
        r.aura._deprecated.aura_20wbtc80badger_2nd_migration
    )
    aura_40wbtc40digg20gravi = vault.contract(r.aura.aura_40wbtc40digg20gravi_gauge)
    aura_40wbtc40digg20gravi_old = vault.contract(
        r.aura._deprecated.aura_40wbtc40digg20gravi_gauge_2nd_migration
    )

    bal_20wbtc80badger = aura_20wbtc80badger_old.balanceOf(vault)
    aura_20wbtc80badger_old.approve(migrator, bal_20wbtc80badger)
    migrator.migrate(18, AURA_NEW_PID_WBTC_BADGER)
    assert aura_20wbtc80badger.balanceOf(vault) == bal_20wbtc80badger

    bal_40wbtc40digg20gravi = aura_40wbtc40digg20gravi_old.balanceOf(vault)
    aura_40wbtc40digg20gravi_old.approve(migrator, bal_40wbtc40digg20gravi)
    migrator.migrate(19, AURA_NEW_PID_WBTC_DIGG_GRAVI)
    assert aura_40wbtc40digg20gravi.balanceOf(vault) == bal_40wbtc40digg20gravi

    vault.post_safe_tx()
