from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# current owner
avatar_owner = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)

# new owner
new_owner = r.badger_wallets.treasury_vault_multisig

# avatars
aura_avatar = avatar_owner.contract(r.avatars.aura)
convex_avatar = avatar_owner.contract(r.avatars.convex)


def main():
    aura_avatar.transferOwnership(new_owner)
    convex_avatar.transferOwnership(new_owner)

    avatar_owner.post_safe_tx()
