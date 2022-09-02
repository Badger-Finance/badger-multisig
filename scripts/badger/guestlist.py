from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import get_registry as registry
from helpers.constants import MaxUint256, AddressZero

C = Console()

# assuming techOps
r = registry()
SAFE = GreatApeSafe(r.badger_wallets.techops_multisig)
SAFE.init_badger()

# Add the vaults addresses to remove caps from
VAULTS_ARRAY = ["0x63ad745506BD6a3E57F764409A47ed004BEc40b1", "0x371B7C451858bd88eAf392B383Df8bd7B8955d5a"]

# Sets a new user cap for a given vault
def set_vault_user_cap(vault, cap):
    vault = SAFE.contract(vault)
    guestlist = vault.guestList()
    if guestlist != AddressZero:
        C.print(f"Guestlist: {guestlist}")
        SAFE.badger.set_guestlist_user_cap(guestlist, cap)
        SAFE.post_safe_tx()
    else:
        C.print(f"[red]No guestlist set for this vault![/red]")

# Sets a new total cap for a given vault
def set_vault_total_cap(vault, cap):
    vault = SAFE.contract(vault)
    guestlist = vault.guestList()
    if guestlist != AddressZero:
        C.print(f"Guestlist: {guestlist}")
        SAFE.badger.set_guestlist_total_cap(guestlist, cap)
        SAFE.post_safe_tx()
    else:
        C.print(f"[red]No guestlist set for this vault![/red]")

# Sets the user and total cap to MAXUINT256 for a given vault
def remove_caps_for_vault(vault):
    vault = SAFE.contract(vault)
    guestlist = vault.guestList()
    if guestlist != AddressZero:
        C.print(f"Guestlist: {guestlist}")
        SAFE.badger.set_guestlist_total_cap(guestlist, int(MaxUint256))
        SAFE.badger.set_guestlist_user_cap(guestlist, int(MaxUint256))
        SAFE.post_safe_tx()
    else:
        C.print(f"[red]No guestlist set for this vault![/red]")

# Sets the user and total cap to MAXUINT256 for a batch of vaults
def remove_caps_for_vaults():
    if VAULTS_ARRAY:
        for vault in VAULTS_ARRAY:
            vault = SAFE.contract(vault)
            C.print(f"Vault: {vault}")
            guestlist = vault.guestList()
            if guestlist != AddressZero:
                C.print(f"Guestlist: {guestlist}")
                SAFE.badger.set_guestlist_total_cap(guestlist, int(MaxUint256))
                SAFE.badger.set_guestlist_user_cap(guestlist, int(MaxUint256))
            else:
                C.print(f"[red]No guestlist set for this vault ({vault})![/red]")
        SAFE.post_safe_tx()
    else:
        C.print(f"[red]Make sure to add your vaults to the array![/red]")