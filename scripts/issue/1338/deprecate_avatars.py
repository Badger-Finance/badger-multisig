from brownie import web3
from decimal import Decimal
from great_ape_safe import GreatApeSafe
from helpers.addresses import r


# https://etherscan.io/address/0x5a92EF27f4baA7C766aee6d751f754EBdEBd9fae#code#L722
MIN_LOCK_TIME = 594000


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_convex()
    vault.init_aura()

    # avatars
    aura_avatar = vault.contract(r.avatars.aura)
    convex_avatar = vault.contract(r.avatars.convex)

    # balancer bpts
    bpt_badgerwbtc = vault.contract(r.balancer.B_20_BTC_80_BADGER)
    bpt_badgerreth = vault.contract(r.balancer.B_50_BADGER_50_RETH)
    bpt_wbtcdigggravi = vault.contract(r.balancer.bpt_40wbtc_40digg_20graviaura)

    # convex wrap lp
    badger_fraxbp = vault.contract(r.treasury_tokens.badgerFRAXBP_f_lp)
    wcvx_badger_fraxbp = vault.contract(r.convex.frax.wcvx_badger_fraxbp)

    # liq out from avatars
    aura_avatar.withdrawAll()

    private_pids = convex_avatar.getPrivateVaultPids()
    if len(private_pids) > 0:
        for pid in private_pids:
            convex_avatar.withdrawFromPrivateVault(pid)

    # deposit in vault directly pos
    vault.aura.deposit_all_and_stake(bpt_badgerwbtc)
    vault.aura.deposit_all_and_stake(bpt_badgerreth)
    vault.aura.deposit_all_and_stake(bpt_wbtcdigggravi)

    lp_balance = badger_fraxbp.balanceOf(vault)
    badger_fraxbp.approve(wcvx_badger_fraxbp, lp_balance)
    wcvx_badger_fraxbp.deposit(lp_balance, vault)

    staking_lp_balance = wcvx_badger_fraxbp.balanceOf(vault)
    vault.convex.stake_lock(
        wcvx_badger_fraxbp,
        staking_lp_balance,
        MIN_LOCK_TIME,
        vault.convex.VAULT_TYPES["badger_fraxbp"],
        # https://etherscan.io/tx/0x74f4492c78385b633fdecb2200efdd99f7377dbf2e0b94468c06682fb78961c1#eventlog (event #214)
        kek_id="FE2A58EC80B5D297700D8FC6B5ED4A0E258DA0CDC27DA72570E7D43FABB2DC4E",
        lock_additional=True,
    )

    # note: leaving the claims and processing for the keepers, since it will be the last one

    vault.post_safe_tx()


def stop_automation():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)

    upkeep_manager = techops.contract(r.badger_wallets.upkeep_manager)

    upkeep_manager.cancelMemberUpkeep(r.avatars.aura)
    upkeep_manager.cancelMemberUpkeep(r.avatars.convex)

    techops.post_safe_tx()
