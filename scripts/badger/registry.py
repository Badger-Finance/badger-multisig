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

    key_set = set()

    key_index = 0
    while True:
        try:
            # # some registry keys are duplicated with surrounding quotes, let's remove and dedup
            key = chain_safe.badger.registry.keys(key_index).replace("\"", "")

            # ignore duplicated sanitized keys, only operate on unique values
            if key not in key_set:
                # smol patchwerk, if we ever need more make a real function (manual migration on new key)
                if key == 'devGovernance':
                    value = chain_safe.badger.registry.get(key)
                    expected_value = contract_registry.badger_wallets.techops_multisig
                    if value != expected_value:
                        raise Exception(f"Invalid key value found on {key}: found {value}, expected: {expected_value}")
                    key = 'techOps'
                    chain_safe.badger.set_key_on_registry(key, value)
                else:
                    chain_safe.badger.migrate_key_on_registry(key)

                key_set.add(key)

            key_index += 1
        except:
            break

    # try to simulate tx and see dafuq
    chain_safe.post_safe_tx()
