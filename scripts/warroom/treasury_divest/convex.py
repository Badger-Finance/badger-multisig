from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_convex()
    vault.init_curve_v2()

    badger_fraxbp = vault.contract(r.treasury_tokens.badgerFRAXBP_f_lp)
    wcvx_badger_fraxbp = vault.contract(r.convex.frax.wcvx_badger_fraxbp)
    frax_usdc = vault.contract(r.treasury_tokens.crvFRAXUSDC)

    badger = vault.contract(r.treasury_tokens.BADGER)
    fxs = vault.contract(r.treasury_tokens.FXS)
    usdc = vault.contract(r.treasury_tokens.USDC)
    frax = vault.contract(r.treasury_tokens.FRAX)

    vault.take_snapshot(tokens=[badger, fxs, usdc, frax])

    pool_id = vault.convex.get_pool_pid(wcvx_badger_fraxbp)
    private_vault = vault.convex.frax_pool_registry.vaultMap(pool_id, vault)
    badger_frax_kek_id = vault.contract(r.frax.BADGER_FRAXBP_GAUGE).lockedStakes(
        private_vault, 0
    )[0]

    vault.convex.withdraw_locked(wcvx_badger_fraxbp, badger_frax_kek_id)
    wcvx_badger_fraxbp.withdrawAndUnwrap(wcvx_badger_fraxbp.balanceOf(vault))
    vault.convex.withdraw_all(badger_fraxbp)
    vault.curve_v2.withdraw(badger_fraxbp, badger_fraxbp.balanceOf(vault))
    vault.curve_v2.withdraw(frax_usdc, frax_usdc.balanceOf(vault))

    vault.post_safe_tx()
