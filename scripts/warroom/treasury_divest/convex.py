from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import Contract, interface

def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_convex()
    vault.init_curve_v2()
    
    badger_fraxbp = vault.contract(r.treasury_tokens.badgerFRAXBP_f_lp)
    wcvx_badger_fraxbp = vault.contract(r.convex.frax.wcvx_badger_fraxbp)
    badger = vault.contract(r.treasury_tokens.BADGER)
    usdc = vault.contract(r.treasury_tokens.USDC)
    frax = vault.contract(r.treasury_tokens.FRAX)
    fxs = vault.contract(r.treasury_tokens.FXS)
    
    vault.take_snapshot(tokens=[badger, usdc, frax, fxs])
    
    # https://etherscan.io/tx/0x74f4492c78385b633fdecb2200efdd99f7377dbf2e0b94468c06682fb78961c1#eventlog (event #214)
    badger_frax_kek_id = "FE2A58EC80B5D297700D8FC6B5ED4A0E258DA0CDC27DA72570E7D43FABB2DC4E"
    vault.convex.withdraw_locked(wcvx_badger_fraxbp, badger_frax_kek_id)
    wcvx_badger_fraxbp.withdrawAndUnwrap(wcvx_badger_fraxbp.balanceOf(vault))
    vault.convex.withdraw_all(badger_fraxbp)
    vault.curve_v2.withdraw(badger_fraxbp, badger_fraxbp.balanceOf(vault))
    
    vault.post_safe_tx()
