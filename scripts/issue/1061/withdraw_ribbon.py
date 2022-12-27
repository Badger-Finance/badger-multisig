from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    ribbon = vault.contract(r.ribbon.badger_vault)
    ribbon.initiateWithdraw(
        100_000e18
    )  # call completeWithdraw permissionlessly once current round is over
    vault.post_safe_tx()
