from brownie import accounts

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    voter = GreatApeSafe(r.badger_wallets.bvecvx_voting_multisig)

    aurabal_staking = voter.contract(r.aura.aurabal_staking)
    aura_locker = voter.contract(r.aura.vlAURA)

    # claim AURA
    aurabal_staking.getReward(True)

    # delegate VP to
    delegate_addr = accounts.at("delegate.badgerdao.eth", force=True).address
    aura_locker.delegate(delegate_addr)

    voter.post_safe_tx()
