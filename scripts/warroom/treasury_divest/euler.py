from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# NOTE: amount avail may differ from posting till exec
EXEC_SLIPPAGE = 0.98


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)

    vault.init_euler()

    badger = vault.contract(r.treasury_tokens.BADGER)
    ebadger = interface.IEToken(vault.euler.markets.underlyingToEToken(badger))

    vault.take_snapshot(tokens=[badger, ebadger])

    badger_total_bal_market = badger.balanceOf(vault.euler.euler)
    badger_wd_amt = badger_total_bal_market * EXEC_SLIPPAGE

    vault.euler.withdraw(badger, badger_wd_amt)

    vault.post_safe_tx()
