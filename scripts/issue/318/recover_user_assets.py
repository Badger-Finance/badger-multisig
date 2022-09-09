from brownie import interface
from decimal import Decimal
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

USER = "0x53ed17651b7dc5131c8878f0c30e6928ff13f8e2"
TREASURY = registry.eth.badger_wallets.treasury_vault_multisig
STUCK_BALANCE = 5267941640682
FEE = 0.2  # Charging a 20% service fee

#
#   Sweeps stuck bSLP tokens stuck on itself, charges a 20% service fee,
#   and transfers reminder to affected user.
#
def main():
    # Sweep() can be called from TechOps but will use Dev in order to handle atomically
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    balance_checker = interface.IBalanceChecker(
        registry.eth.helpers.balance_checker, owner=safe.account
    )

    vault = interface.ISettV4h(
        registry.eth.sett_vaults["bslpWbtcibBTC"], owner=safe.account
    )

    balance_gov_before = vault.balanceOf(safe.account)
    balance_vault_before = vault.balanceOf(vault.address)
    assert balance_vault_before == STUCK_BALANCE

    # Sweep assets
    vault.sweep(vault.address)

    balance_gov_after = vault.balanceOf(safe.account)
    balance_vault_after = vault.balanceOf(vault.address)
    assert balance_vault_after == 0
    assert balance_gov_after - balance_gov_before == STUCK_BALANCE

    balance_checker.verifyBalance(vault.address, safe.account, balance_gov_after)

    # Process fee
    fee_amount = round(STUCK_BALANCE * FEE)
    vault.transfer(TREASURY, fee_amount)

    # Transfer reminder to user
    reminder = vault.balanceOf(safe.account) - balance_gov_before

    assert reminder == STUCK_BALANCE - fee_amount

    vault.transfer(USER, reminder)

    print("Fee", fee_amount)
    print("Reminder", reminder)

    safe.post_safe_tx()
