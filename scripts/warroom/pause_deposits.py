from great_ape_safe import GreatApeSafe
from helpers.addresses import r

def main(vault_address):
    """
    Pauses deposits on a given Vault V1.5 governed by the Dev Multisig
    """
    dev = GreatApeSafe(r.badger_wallets.dev_multisig)
    dev.init_badger()

    dev.badger.pause_deposits(vault_address)

    dev.post_safe_tx()
