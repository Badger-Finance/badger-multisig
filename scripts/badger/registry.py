from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import get_registry as registry

console = Console()

# assuming techOps
contract_registry = registry()
chain_safe = GreatApeSafe(contract_registry.badger_wallets.techops_multisig)
chain_safe.init_badger()

def set_key(key, target_addr):
    """
    Sets the input target address on the registry under the specified 'key' 
    """

    chain_safe.badger.set_key_on_registry(key, target_addr)
    chain_safe.post_safe_tx()

def migrate_registry_keys():
    """
    Migrate badger registry v1 keys on a given chain to badger registry v2
    """

    key_index = 0
    while True:
        try:
            key = chain_safe.badger.registry.keys(key_index)

            # smol patchwerk, if we ever need more make a real function
            if key == 'devGovernance':
                key = 'techOps'
        except:
            break
        chain_safe.badger.migrate_key_on_registry(key)
        key_index += 1

    # try to simulate tx and see dafuq
    chain_safe.post_safe_tx()
