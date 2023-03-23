from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# flag
max_out_wd = False

# NOTE: amount avail may differ from posting till exec
EXEC_SLIPPAGE = 0.95


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)

    vault.init_euler()

    badger = vault.contract(r.treasury_tokens.BADGER)
    ebadger = interface.IEToken(vault.euler.markets.underlyingToEToken(badger))
    dbadger = interface.IDebtToken(vault.euler.markets.underlyingToDToken(badger))

    vault.take_snapshot(tokens=[badger, ebadger])

    ebadger_total_supply = ebadger.totalSupply()
    ebadger_vault_balance = ebadger.balanceOf(vault)

    badger_total_bal_market = badger.balanceOf(vault.euler.euler)

    utilisation_rate = dbadger.totalSupply() / ebadger_total_supply
    market_ownership_rate = ebadger_vault_balance / ebadger_total_supply

    print(
        f"Market utilisation: {utilisation_rate:2%}. Market ownership: {market_ownership_rate:.2%}"
    )

    if max_out_wd:
        # NOTE: this represents a max out of whichever amount is idle in the market to wd
        # https://etherscan.io/token/0x3472A5A71965499acd81997a54BBA8D852C6E53d?a=0x27182842E098f60e3D576794A5bFFb0777E025d3
        badger_wd_amt = min(
            badger_total_bal_market * EXEC_SLIPPAGE, ebadger_vault_balance
        )
    else:
        # NOTE: this represents a softer wd approach consider our percetange of market ownership and utilisation rate
        badger_wd_amt = (
            ebadger_total_supply * (1 - utilisation_rate) * (1 - market_ownership_rate)
        )

    vault.euler.withdraw(badger, badger_wd_amt)

    vault.post_safe_tx()
