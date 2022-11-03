from argparse import REMAINDER
from brownie import chain, Contract
from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console
import time

C = Console()

DEV = r.badger_wallets.dev_multisig
TECH_OPS = r.badger_wallets.techops_multisig
BVE_OXD = r.sett_vaults.bveOXD
BVE_OXD_LP = r.sett_vaults.bbveOXD_OXD
BVE_OXD_STRAT = r.strategies["native.vestedOXD"]

# Thu Oct 27 2022 17:42:29 GMT+0000 (To be safe, unlocks on the 26th)
UNLOCKTIME = 1666892549

# Remaining amount: OXD that has been relocked from harvests ever since earns stopped 
# To be unlocked on 	Thu Feb 09 2023 00:00:00 GMT+0000 (1675900800)
REMAINDER = 144966162970875359338

def process_final_locks(simulation="false"):
    safe = GreatApeSafe(DEV)

    bveoxd_strat = safe.contract(BVE_OXD_STRAT)
    bveoxd_vault = safe.contract(BVE_OXD)
    oxd = safe.contract(bveoxd_strat.want())

    # Process expired locks and withdraw all OXD to vault

    if simulation == "true":
        chain.sleep(1666892549 - int(time.time()))

    total_balance = bveoxd_vault.balance()
    vault_balance_before = oxd.balanceOf(bveoxd_vault)
    strat_balance_before = oxd.balanceOf(bveoxd_strat)
    pool_balance_before = bveoxd_strat.balanceOfPool()
    assert total_balance == vault_balance_before + strat_balance_before + pool_balance_before

    # Processing last lock, all balance should be withdrawn to strat
    bveoxd_strat.prepareWithdrawAll()
    assert oxd.balanceOf(bveoxd_strat) == strat_balance_before + pool_balance_before - REMAINDER
    assert bveoxd_strat.balanceOfPool() == REMAINDER

    # Send all OXD to vault
    bveoxd_strat.manualSendOXDToVault()
    assert oxd.balanceOf(bveoxd_strat) == 0
    assert oxd.balanceOf(bveoxd_vault) == total_balance - REMAINDER

    safe.post_safe_tx()


def deprecate_fantom_vaults():
    safe = GreatApeSafe(TECH_OPS)
    safe.init_badger()

    # Deprecate vaults on RegistryV2
    safe.badger.demote_vault(BVE_OXD, 0)
    safe.badger.demote_vault(BVE_OXD_LP, 0)

    safe.post_safe_tx()
