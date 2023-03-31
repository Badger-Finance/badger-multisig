from brownie import chain

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main(sim=False):
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
            if sim:
                # min lock time: https://etherscan.io/address/0x5a92ef27f4baa7c766aee6d751f754ebdebd9fae#code#L722
                chain.sleep(604800)
                chain.mine()
            convex_avatar.withdrawFromPrivateVault(pid)

    vanilla_convex_pids = convex_avatar.getPids()
    if len(vanilla_convex_pids) > 0:
        convex_avatar.withdrawAll()

    if not sim:
        techops.post_safe_tx()
    else:
        techops.post_safe_tx(skip_preview=True)
