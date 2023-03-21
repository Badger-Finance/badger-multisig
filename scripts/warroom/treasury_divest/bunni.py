from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import Contract, interface

def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_bunni(r.bunni.badger_wbtc_bunni_token)
    
    wbtc = vault.contract(r.treasury_tokens.WBTC)
    badger = vault.contract(r.treasury_tokens.BADGER)
    
    vault.take_snapshot(tokens=[vault.bunni.bunni_token, wbtc, badger])
    
    vault.bunni.withdraw()

    vault.post_safe_tx()
