from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    wbtc = vault.contract(r.treasury_tokens.WBTC)
    badger = vault.contract(r.treasury_tokens.BADGER)
    aura = vault.contract(r.treasury_tokens.AURA)
    bal = vault.contract(r.treasury_tokens.BAL)
    graviaura = vault.contract(r.sett_vaults.graviAURA)
    fxs = vault.contract(r.treasury_tokens.FXS)
    comp = vault.contract(r.treasury_tokens.COMP)
    frax = vault.contract(r.treasury_tokens.FRAX)
    bvecvx = vault.contract(r.treasury_tokens.bveCVX)
    b80bal20weth = vault.contract(r.balancer.B_80_BAL_20_WETH)
    bbausd = vault.contract(r.balancer.BB_A_USD)

    sweep = [aura, bal, graviaura, fxs, comp, frax, b80bal20weth, bbausd]

    vault.take_snapshot([wbtc, badger, bvecvx] + sweep)

    vault.init_uni_v3()
    vault.uni_v3.collect_fees()

    for token in sweep:
        token.transfer(r.badger_wallets.treasury_ops_multisig, token.balanceOf(vault))

    bvecvx.transfer(r.badger_wallets.treasury_voter_multisig, token.balanceOf(vault))

    vault.post_safe_tx(call_trace=True)
