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

    key_replacements = {
        'devGovernance': 'techOps',
        'timelock': 'governanceTimelock',
    }

    key_lookups = {
        'techOps': contract_registry.badger_wallets.techops_multisig,
        'governanceTimelock': contract_registry.governance_timelock,
    }

    key_set = set()

    key_index = 0
    while True:
        try:
            # # some registry keys are duplicated with surrounding quotes, let's remove and dedup
            key = chain_safe.badger.registry.keys(key_index).replace("\"", "")

            # ignore duplicated sanitized keys, only operate on unique values
            if key not in key_set:
                should_replace = key in key_replacements
                print(f"Migrating new unique key: {key} {'with' if should_replace else 'without'} replacement")
                if should_replace:
                    value = chain_safe.badger.registry.get(key)
                    key = key_replacements[key]
                    if key in key_lookups:
                        value = key_lookups[key]
                    chain_safe.badger.set_key_on_registry(key, value)
                else:
                    chain_safe.badger.migrate_key_on_registry(key)

                key_set.add(key)

            key_index += 1
        except Exception as e:
            print(e)
            break

    # try to simulate tx and see dafuq
    chain_safe.post_safe_tx()
