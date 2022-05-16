from helpers.addresses import registry
from great_ape_safe import GreatApeSafe


def main():
    safe = GreatApeSafe(registry.arbitrum.badger_wallets.dev_multisig)
    bDXS = safe.contract(registry.arbitrum.sett_vaults.bdxsSwaprWeth)
    safe.take_snapshot(tokens=[bDXS])

    bDXS.withdrawAll()

    safe.print_snapshot()
    safe.post_safe_tx()
