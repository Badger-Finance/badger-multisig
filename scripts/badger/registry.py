from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import r

C = Console()

# assuming techOps
SAFE = GreatApeSafe(r.badger_wallets.techops_multisig)
SAFE.init_badger()

# Allowed metadata behaviors
# NOTE: Should be kept up to date matching the behaviors defined on the SDK at
# https://github.com/Badger-Finance/badger-sdk/blob/main/src/vaults/enums/vault-behavior.enum.ts
ALLOWED_BEHAVIORS = [
    "Compounder",
    "Helper",
    "DCA",
    "Ecosystem",
    "Ecosystem Helper",
    "None",
]

# Add any vaults's addresses with their corresponding new status to demote or promote to
VAULTS_STATUS = {
    "0x0000000000000000000000000000000000000000": 0,
}

# Add your keys and addresses to add to the registry in a batch
KEYS_ADDRESSES = {
    "test_key": "0x0000000000000000000000000000000000000000",
}

# promote or demote a batch of vaults given their addresses and new status
def update_vault_status():
    if VAULTS_STATUS:
        for vault, new_status in VAULTS_STATUS.items():
            info = SAFE.badger.registry_v2.productionVaultInfoByVault(vault).dict()
            if info["status"] < new_status:
                SAFE.badger.promote_vault(
                    info["vault"], info["version"], info["metadata"], new_status
                )
                assert (
                    SAFE.badger.registry_v2.productionVaultInfoByVault(vault).dict()[
                        "status"
                    ]
                    == new_status
                )
                C.print(f"[green]Promoting {vault} to {new_status}[/green]")
            else:
                SAFE.badger.demote_vault(vault, new_status)
                assert (
                    SAFE.badger.registry_v2.productionVaultInfoByVault(vault).dict()[
                        "status"
                    ]
                    == new_status
                )
                C.print(f"[green]Demoting {vault} to {new_status}[/green]")
        SAFE.post_safe_tx()
    else:
        C.print(f"[red]Make sure to add your vaults and status to the arrays![/red]")


# change a vault's metadata given a vault address and the new matadata
# Both the vault address and metadata can be passed as strings from the console.
# NOTE: If metadata includes spaces, it can be passed using single quotation marks
# Example of call: brownie run scripts/badger/registry.py update_vault_metadata
# 0x37d9D2C6035b744849C15F1BFEE8F268a20fCBd8 'name=auraBAL,protocol=Aura,behavior=None'
def update_vault_metadata(vault, metadata):
    # Ensure that the new Behavior is allowed
    if "behavior=" in metadata:
        new_behavior = metadata.split("behavior=")[1]
        if new_behavior not in ALLOWED_BEHAVIORS:
            C.print(
                f"[red]Wrong vault behavior! Allowed behaviors: {ALLOWED_BEHAVIORS}[/red]"
            )
            return
    else:
        C.print(f"[red]Wrong metadata format[/red]")
        return

    current_metadata = SAFE.badger.registry_v2.productionVaultInfoByVault(vault).dict()[
        "metadata"
    ]
    C.print(f"Current metadata: {current_metadata}")
    C.print(f"New metadata: {metadata}")

    SAFE.badger.update_metadata(vault, metadata)
    current_metadata = SAFE.badger.registry_v2.productionVaultInfoByVault(vault).dict()[
        "metadata"
    ]
    assert current_metadata == metadata

    SAFE.post_safe_tx()


def set_key(key, target_addr):
    """
    Sets the input target address on the registry under the specified 'key'
    """

    SAFE.badger.set_key_on_registry(key, target_addr)
    SAFE.post_safe_tx()


def set_keys():
    """
    For each entry on the dictionary "KEYS_ADDRESSES", sets the input target
    address on the registry under the specified 'key'
    """
    for key, target_addr in KEYS_ADDRESSES.items():
        SAFE.badger.set_key_on_registry(key, target_addr)

    SAFE.post_safe_tx()


def migrate_registry_keys():
    """
    Migrate badger registry v1 keys on a given chain to badger registry v2
    """

    key_replacements = {
        "devGovernance": "techOps",
        "timelock": "governanceTimelock",
    }

    key_lookups = {
        "techOps": r.badger_wallets.techops_multisig,
        "governanceTimelock": r.governance_timelock,
    }

    key_set = set()

    key_index = 0
    while True:
        try:
            # # some registry keys are duplicated with surrounding quotes, let's remove and dedup
            key = SAFE.badger.registry.keys(key_index).replace('"', "")

            # ignore duplicated sanitized keys, only operate on unique values
            if key not in key_set:
                should_replace = key in key_replacements
                print(
                    f"Migrating new unique key: {key} {'with' if should_replace else 'without'} replacement"
                )
                if should_replace:
                    value = SAFE.badger.registry.get(key)
                    key = key_replacements[key]
                    if key in key_lookups:
                        value = key_lookups[key]
                    SAFE.badger.set_key_on_registry(key, value)
                else:
                    SAFE.badger.migrate_key_on_registry(key)

                key_set.add(key)

            key_index += 1
        except Exception as e:
            print(e)
            break

    # try to simulate tx and see dafuq
    SAFE.post_safe_tx()
