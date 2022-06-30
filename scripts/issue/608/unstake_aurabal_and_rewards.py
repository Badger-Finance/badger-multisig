from brownie import accounts

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    voter.take_snapshot(tokens=[r.treasury_tokens.AURABAL])

    aurabal_staking = voter.contract(r.aura.aurabal_staking)

    aurabal_staking.withdraw(aurabal_staking.balanceOf(voter), True, True)
    assert aurabal_staking.balanceOf(voter) == 0

    voter.post_safe_tx()
