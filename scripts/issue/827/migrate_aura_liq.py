from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    migrator = vault.contract(r.aura.gauge_migrator)
    aura_20wbtc80badger = vault.contract(r.aura.aura_20wbtc80badger)
    aura_20wbtc80badger_old = vault.contract(r.aura.aura_20wbtc80badger_old)
    aura_40wbtc40digg20gravi = vault.contract(r.aura.aura_40wbtc40digg20gravi)
    aura_40wbtc40digg20gravi_old = vault.contract(r.aura.aura_40wbtc40digg20gravi_old)

    bal_20wbtc80badger = aura_20wbtc80badger_old.balanceOf(vault)
    aura_20wbtc80badger_old.approve(migrator, bal_20wbtc80badger)
    migrator.migrate(11, 33)
    # confirm our balance was migrated to the new gauge token
    assert aura_20wbtc80badger.balanceOf(vault) == bal_20wbtc80badger

    bal_40wbtc40digg20gravi = aura_40wbtc40digg20gravi_old.balanceOf(vault)
    aura_40wbtc40digg20gravi_old.approve(migrator, bal_40wbtc40digg20gravi)
    migrator.migrate(18, 34)
    # confirm balance
    assert aura_40wbtc40digg20gravi.balanceOf(vault) == bal_40wbtc40digg20gravi

    vault.post_safe_tx()
