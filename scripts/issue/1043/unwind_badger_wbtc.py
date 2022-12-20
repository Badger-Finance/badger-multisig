from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_curve_v2()

    crvbadger_wbtc = vault.contract(r.treasury_tokens.badgerWBTC_f)
    bcrv_badger_wbtc = interface.ISettV4h(r.sett_vaults.bcrvBadger, owner=vault.account)

    badger = vault.contract(r.treasury_tokens.BADGER)
    wbtc = vault.contract(r.treasury_tokens.WBTC)

    vault.take_snapshot(tokens=[crvbadger_wbtc, bcrv_badger_wbtc, badger, wbtc])

    bcrv_badger_wbtc.withdrawAll()
    vault.curve_v2.withdraw(crvbadger_wbtc, crvbadger_wbtc.balanceOf(vault))

    vault.print_snapshot()
    vault.post_safe_tx()
