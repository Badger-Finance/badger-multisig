from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import Contract, interface

def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_aura()
    vault.init_balancer()
    
    badger = vault.contract(r.treasury_tokens.BADGER)
    wbtc = vault.contract(r.treasury_tokens.WBTC)
    weth = vault.contract(r.treasury_tokens.WETH)
    reth = vault.contract(r.treasury_tokens.RETH)
    digg = vault.contract(r.treasury_tokens.DIGG)
    aura = vault.contract(r.treasury_tokens.AURA)
    bal = vault.contract(r.treasury_tokens.BAL)
    graviaura = vault.contract(r.sett_vaults.graviAURA)
    
    vault.take_snapshot(tokens=[badger, wbtc, weth, reth, digg, aura, bal, graviaura])

    aura_bpts = [
        vault.contract(r.balancer.B_20_BTC_80_BADGER),
        vault.contract(r.balancer.bpt_40wbtc_40digg_20graviaura),
        vault.contract(r.balancer.B_50_BADGER_50_RETH)
    ]

    for bpt in aura_bpts:
        vault.aura.unstake_all_and_withdraw_all(bpt)
        vault.balancer.unstake_all_and_withdraw_all(pool=bpt, unstake=False)
        
    vault.post_safe_tx()
    