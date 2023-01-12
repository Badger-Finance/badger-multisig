from great_ape_safe import GreatApeSafe
from helpers.addresses import r

from brownie import interface


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_balancer()

    baurabal = interface.ITheVault(r.sett_vaults.bauraBal, owner=vault.address)
    aurabal = vault.contract(r.treasury_tokens.AURABAL)
    bal80_20weth = vault.contract(r.balancer.B_80_BAL_20_WETH)
    weth = vault.contract(r.treasury_tokens.WETH)
    stable_pool = vault.contract(r.balancer.B_auraBAL_STABLE)

    vault.take_snapshot(tokens=[baurabal.address, weth])

    # 1. undog sett
    baurabal.withdrawAll()

    # 2. swap for bal80-20weth
    vault.balancer.swap(
        aurabal, bal80_20weth, aurabal.balanceOf(vault), pool=stable_pool
    )

    # 3. wd to single asset `weth`
    vault.balancer.unstake_and_withdraw_all_single_asset(
        weth, pool=bal80_20weth, unstake=False
    )

    vault.post_safe_tx(skip_preview=True)
