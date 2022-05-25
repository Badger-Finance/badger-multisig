from brownie import web3
from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


console = Console()

# assuming techOps
SAFE = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
SAFE.init_badger()

def set_key(key, target_addr):
    """
    Sets the input target address on the registry under the specified 'key' 
    """

    SAFE.badger.set_key_on_registry(key, target_addr)
    SAFE.post_safe_tx()

def migrate_registry_keys():
    """
    Migrate badger registry v1 keys on a given chain to badger registry v2
    """
    key_index = 0
    while True:
        try:
            key = SAFE.badger.registry.keys(key_index)
            SAFE.badger.migrate_key_on_registry(key)
            key_index += 1
        except:
            break

    # try to simulate tx and see dafuq
    SAFE.post_safe_tx(False, True, True, True, False, False, None, None, None, 1.5)

