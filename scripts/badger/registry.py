from rich.console import Console
from great_ape_safe import GreatApeSafe
import click
from helpers.addresses import get_registry as registry

console = Console()

# assuming techOps
r = registry()
safe = GreatApeSafe(r.badger_wallets.techops_multisig)
safe.init_badger()

def set_key(key, target_addr):
    """
    Sets the input target address on the registry under the specified 'key' 
    """

    safe.badger.set_key_on_registry(key, target_addr)
    safe.post_safe_tx()

def migrate_registry_keys():
    """
    Migrate badger registry v1 keys on a given chain to badger registry v2
    """

    key_replacements = {
        'devGovernance': 'techOps',
        'timelock': 'governanceTimelock',
    }

    key_lookups = {
        'techOps': r.badger_wallets.techops_multisig,
        'governanceTimelock': r.governance_timelock,
    }

    key_set = set()

    key_index = 0
    while True:
        try:
            # # some registry keys are duplicated with surrounding quotes, let's remove and dedup
            key = safe.badger.registry.keys(key_index).replace("\"", "")

            # ignore duplicated sanitized keys, only operate on unique values
            if key not in key_set:
                should_replace = key in key_replacements
                print(f"Migrating new unique key: {key} {'with' if should_replace else 'without'} replacement")
                if should_replace:
                    value = safe.badger.registry.get(key)
                    key = key_replacements[key]
                    if key in key_lookups:
                        value = key_lookups[key]
                    safe.badger.set_key_on_registry(key, value)
                else:
                    safe.badger.migrate_key_on_registry(key)

                key_set.add(key)

            key_index += 1
        except Exception as e:
            print(e)
            break

    # try to simulate tx and see dafuq
    safe.post_safe_tx()



# promote a batch of vaults given their addresses and new status
def promote_vaults(vaults_array, new_status_array):
    for vault in vaults_array:
        info = safe.badger.registry_v2.productionVaultInfoByVault(vault)
        new_status = new_status_array[vaults_array.index(vault)]
        if info[2] < new_status:
            safe.badger.promote_vault(info[0], info[1], info[3], new_status)
            assert safe.badger.registry_v2.productionVaultInfoByVault(vault)[2] == new_status
            console.print(f"[green]Promoting {vault} to {new_status}[/green]")
        else:
            console.print(f"[red]Promoting {vault} to lower state, current state is {info[2]}[/red]")
    safe.post_safe_tx()



# demote a batch of vaults given their addresses and new status
def demote_vaults(vaults_array, new_status_array):
    for vault in vaults_array:
        info = safe.badger.registry_v2.productionVaultInfoByVault(vault)
        new_status = new_status_array[vaults_array.index(vault)]
        if info[2] < new_status:
            safe.badger.demote_vault(vault, new_status)
            assert safe.badger.registry_v2.productionVaultInfoByVault(vault)[2] == new_status
            console.print(f"[green]Demoting {vault} to {new_status}[/green]")
        else:
            console.print(f"[red]Demoting to higher state, current state is {info[2]}[/red]")
    safe.post_safe_tx()


# interactive cli function that allows to change a vault's metadata with ease from options
def update_vault_metadata(vault, metadata):
    info = safe.badger.registry_v2.productionVaultInfoByVault(vault)
    console.print(f"Current metadata: {info[3]}")
    console.print(f"New metadata: {metadata}")

    safe.badger.update_metadata(vault, metadata)
    info = safe.badger.registry_v2.productionVaultInfoByVault(vault)
    assert info[3] == metadata

    safe.post_safe_tx()