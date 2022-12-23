from brownie import run as run_script

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_aura()
    bpts = [
        vault.contract(r.balancer.B_20_BTC_80_BADGER),
        vault.contract(r.balancer.B_50_BADGER_50_RETH),
        vault.contract(r.balancer.bpt_40wbtc_40digg_20graviaura),
    ]
    old_balancer_gauges = [
        vault.contract(r.balancer._deprecated.B_20_BTC_80_BADGER_GAUGE),
        vault.contract(r.balancer._deprecated.B_50_BADGER_50_RETH_GAUGE),
        vault.contract(r.balancer._deprecated.B_40_WBTC_40_DIGG_20_GRAVI_GAUGE),
    ]
    new_aura_gauges = [
        vault.contract(r.aura.aura_20wbtc80badger_gauge),
        vault.contract(r.aura.aura_40wbtc40digg20gravi_gauge),
        vault.contract(r.aura.aura_50reth50badger_gauge),
    ]

    vault.take_snapshot(bpts + new_aura_gauges)

    for gauge in old_balancer_gauges:
        gauge.withdraw(gauge.balanceOf(vault))

    vault.print_snapshot()

    # NOTE: i commented the `post_safe_tx` out of this script:
    run_script("scripts/issue/1048/double_down_on_badgerreth.py")

    vault.print_snapshot()

    for bpt in bpts:
        vault.aura.deposit_all_and_stake(bpt)

    vault.post_safe_tx()
