from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# Here are exceptions that may exist during migration
PID_AURA_MIGRATION_EXCLUDE = 67
PID_CONVEX_MIGRATION_EXCLUDE = 0

# New pids
AURA_NEW_PID_WBTC_BADGER = 111  # https://app.aura.finance/#/pool/111
AURA_NEW_PID_WBTC_DIGG_GRAVI = 112  # https://app.aura.finance/#/pool/112


def sim():
    # ownership transfer
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)

    # avatars
    aura_avatar = trops.contract(r.avatars.aura)
    convex_avatar = trops.contract(r.avatars.convex)

    aura_avatar.transferOwnership(r.badger_wallets.treasury_vault_multisig)
    convex_avatar.transferOwnership(r.badger_wallets.treasury_vault_multisig)

    main(True, True, True)


def main(aura_migration=True, convex_migration=True, treasury_wd=True):
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_aura()

    # boosters
    aura_booster = vault.contract(r.aura.booster)

    # avatars
    aura_avatar = vault.contract(r.avatars.aura)
    convex_avatar = vault.contract(r.avatars.convex)

    # balancer bpts
    bpt_badgerwbtc = vault.contract(r.balancer.B_20_BTC_80_BADGER)
    bpt_badgerreth = vault.contract(r.balancer.B_50_BADGER_50_RETH)
    bpt_wbtcdigggravi = vault.contract(r.balancer.bpt_40wbtc_40digg_20graviaura)

    # convex private vault
    private_vault = vault.contract(r.convex.frax.private_vaults.badger_fraxbp)

    # convex wrap lp
    wcvx_badger_fraxbp = vault.contract(r.convex.frax.wcvx_badger_fraxbp)

    # snap
    vault.take_snapshot(
        tokens=[bpt_badgerwbtc, bpt_badgerreth, bpt_wbtcdigggravi, wcvx_badger_fraxbp]
    )

    if treasury_wd:
        # aura wds
        vault.aura.unstake_all_and_withdraw_all(bpt_badgerwbtc, claim=0)
        vault.aura.unstake_all_and_withdraw_all(bpt_badgerreth, claim=0)
        vault.aura.unstake_all_and_withdraw_all(bpt_wbtcdigggravi, claim=0)

        # convex private wds
        staking_contract = vault.contract(private_vault.stakingAddress())
        kek_id = staking_contract.lockedStakes(private_vault, 0)[0]
        private_vault.withdrawLocked(kek_id)

        vault.print_snapshot()

    if aura_migration:
        total_assets = list(aura_avatar.totalAssets())

        pids = list(aura_avatar.getPids())
        if PID_AURA_MIGRATION_EXCLUDE != 0:
            is_shutdown = aura_booster.poolInfo(PID_AURA_MIGRATION_EXCLUDE)[5]
            if not is_shutdown:
                exception_pid_idx = pids.index(PID_AURA_MIGRATION_EXCLUDE)
                pids.pop(exception_pid_idx)
                total_assets.pop(exception_pid_idx)

        aura_avatar.withdraw(pids, total_assets)
        for pid in pids:
            is_shutdown = aura_booster.poolInfo(pid)[5]
            if is_shutdown:
                aura_avatar.removeBptPositionInfo(pid)

        for new_pid in [AURA_NEW_PID_WBTC_BADGER, AURA_NEW_PID_WBTC_DIGG_GRAVI]:
            aura_avatar.addBptPositionInfo(new_pid)

        bpt_badgerwbtc_balance = bpt_badgerwbtc.balanceOf(vault)
        bpt_badgerreth_balance = bpt_badgerreth.balanceOf(vault)
        bpt_wbtcdigggravi_balance = bpt_wbtcdigggravi.balanceOf(vault)

        bpt_badgerwbtc.approve(aura_avatar, bpt_badgerwbtc_balance)
        bpt_badgerreth.approve(aura_avatar, bpt_badgerreth_balance)
        bpt_wbtcdigggravi.approve(aura_avatar, bpt_wbtcdigggravi_balance)

        bpts_balances = [
            bpt_badgerwbtc_balance,
            bpt_wbtcdigggravi_balance,
            bpt_badgerreth_balance,
        ]
        pids = [
            AURA_NEW_PID_WBTC_BADGER,
            AURA_NEW_PID_WBTC_DIGG_GRAVI,
            PID_AURA_MIGRATION_EXCLUDE,
        ]

        aura_avatar.deposit(pids, bpts_balances)

    if convex_migration:
        staking_lp_balance = wcvx_badger_fraxbp.balanceOf(vault)
        wcvx_badger_fraxbp.approve(convex_avatar, staking_lp_balance)
        convex_avatar.depositInPrivateVault(
            convex_avatar.getPrivateVaultPids()[0], staking_lp_balance, True
        )

    # NOTE: getting `GS013` when not skipping preview - sim
    vault.post_safe_tx(skip_preview=True)
