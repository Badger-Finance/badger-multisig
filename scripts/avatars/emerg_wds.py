from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)

    # avatars
    aura_avatar = techops.contract(r.avatars.aura)
    convex_avatar = techops.contract(r.avatars.convex)

    # withdraws
    vanilla_aura_pids = aura_avatar.getPids()
    if len(vanilla_aura_pids) > 0:
        aura_avatar.withdrawAll()

    private_pids = convex_avatar.getPrivateVaultPids()
    if len(private_pids) > 0:
        for pid in private_pids:
            convex_avatar.withdrawFromPrivateVault(pid)

    vanilla_convex_pids = convex_avatar.getPids()
    if len(vanilla_convex_pids) > 0:
        convex_avatar.withdrawAll()

    techops.post_safe_tx()
