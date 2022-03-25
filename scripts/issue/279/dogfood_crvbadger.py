from brownie import Contract, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)

    crvbadger = interface.ICurveTokenV5(
        registry.eth.treasury_tokens.badgerWBTC_f, owner=safe.account
    )
    bcrvbadger = interface.ISettV4h(
        registry.eth.sett_vaults.bcrvBadger, owner=safe.account
    )

    vault.take_snapshot([crvbadger, bcrvbadger])
    safe.take_snapshot([crvbadger, bcrvbadger])
    bal_crvbadger = crvbadger.balanceOf(safe)
    crvbadger.approve(bcrvbadger, bal_crvbadger)
    bcrvbadger.depositFor(vault, bal_crvbadger)
    vault.print_snapshot()
    safe.print_snapshot()
    safe.post_safe_tx(call_trace=True)
