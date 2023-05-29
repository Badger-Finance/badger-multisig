from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    payments = GreatApeSafe(r.badger_wallets.payments_multisig)
    rem_dripper = GreatApeSafe(r.drippers.rembadger_2023)
    tree_dripper = GreatApeSafe(r.drippers.tree_2023)
    tree = GreatApeSafe(r.badger_wallets.badgertree)

    badger = vault.contract(r.treasury_tokens.BADGER)
    usdc = vault.contract(r.treasury_tokens.USDC)

    vault.take_snapshot([badger, usdc])
    trops.take_snapshot([badger, usdc])
    payments.take_snapshot([badger, usdc])
    rem_dripper.take_snapshot([badger, usdc])
    tree_dripper.take_snapshot([badger, usdc])
    tree.take_snapshot([badger, usdc])

    badger.transfer(tree, 55_000e18)
    badger.transfer(rem_dripper, 300_000e18)
    badger.transfer(tree_dripper, 400_000e18)
    badger.transfer(trops, 45_000e18)
    badger.transfer(payments, 107_000e18)
    usdc.transfer(payments, 265_000e6)

    trops.print_snapshot()
    payments.print_snapshot()
    rem_dripper.print_snapshot()
    tree_dripper.print_snapshot()
    tree.print_snapshot()

    vault.post_safe_tx()
