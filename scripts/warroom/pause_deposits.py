from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# Add the vaults' addresses that you wish to pause deposits on
VAULTS_ARRAY = []

def main():
    """
    Pauses deposits on a given Vault V1.5 governed by the Dev Multisig
    """
    dev = GreatApeSafe(r.badger_wallets.dev_multisig)
    dev.init_badger()

    for vault_address in VAULTS_ARRAY:
        dev.badger.pause_deposits(vault_address)

    dev.post_safe_tx()
