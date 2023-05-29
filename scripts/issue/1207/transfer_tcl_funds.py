from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# Percetange of tcl to be transfer to recipient
PCT_TCL = 1 / 3


def tcl_to_trops():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)

    # underlyings
    lp_badger_wbtc = vault.contract(r.balancer.B_20_BTC_80_BADGER)
    lp_badget_reth = vault.contract(r.balancer.B_50_BADGER_50_RETH)
    lp_gravi_digg = vault.contract(r.balancer.bpt_40wbtc_40digg_20graviaura)

    # snaps
    trops.take_snapshot(tokens=[lp_badger_wbtc, lp_badget_reth, lp_gravi_digg])

    # rewards
    aura_20wbtc80badger_gauge = vault.contract(
        r.aura.aura_20wbtc80badger_gauge,
    )
    aura_40wbtc40digg20gravi_gauge = vault.contract(
        r.aura.aura_40wbtc40digg20gravi_gauge
    )
    aura_50reth50badger_gauge = vault.contract(r.aura.aura_50reth50badger_gauge)

    # wds
    aura_20wbtc80badger_gauge.withdrawAndUnwrap(
        aura_20wbtc80badger_gauge.balanceOf(vault) * PCT_TCL, 0
    )
    aura_40wbtc40digg20gravi_gauge.withdrawAndUnwrap(
        aura_40wbtc40digg20gravi_gauge.balanceOf(vault) * PCT_TCL, 0
    )
    aura_50reth50badger_gauge.withdrawAndUnwrap(
        aura_50reth50badger_gauge.balanceOf(vault) * PCT_TCL, 0
    )

    # recipient transfers
    lp_badger_wbtc.transfer(trops, lp_badger_wbtc.balanceOf(vault))
    lp_badget_reth.transfer(trops, lp_badget_reth.balanceOf(vault))
    lp_gravi_digg.transfer(trops, lp_gravi_digg.balanceOf(vault))

    trops.print_snapshot()
    vault.post_safe_tx()


def avatar_deposits():
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)

    # bpts
    bpt_badgerwbtc = trops.contract(r.balancer.B_20_BTC_80_BADGER)
    bpt_badgerreth = trops.contract(r.balancer.B_50_BADGER_50_RETH)
    bpt_wbtcdigggravi = trops.contract(r.balancer.bpt_40wbtc_40digg_20graviaura)

    # avatar
    aura_avatar = trops.contract(r.avatars.aura)

    bpt_badgerwbtc_balance = bpt_badgerwbtc.balanceOf(trops)
    bpt_badgerreth_balance = bpt_badgerreth.balanceOf(trops)
    bpt_wbtcdigggravi_balance = bpt_wbtcdigggravi.balanceOf(trops)

    bpt_badgerwbtc.approve(aura_avatar, bpt_badgerwbtc_balance)
    bpt_badgerreth.approve(aura_avatar, bpt_badgerreth_balance)
    bpt_wbtcdigggravi.approve(aura_avatar, bpt_wbtcdigggravi_balance)

    bpts_balances = [
        bpt_badgerwbtc_balance,
        bpt_wbtcdigggravi_balance,
        bpt_badgerreth_balance,
    ]
    aura_avatar.deposit(
        aura_avatar.getPids(),
        bpts_balances,
    )

    trops.post_safe_tx(skip_preview=True)
