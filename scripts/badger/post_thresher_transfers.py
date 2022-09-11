from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)

    # tokens
    BCVXCRV = interface.ISettV4h(r.sett_vaults.bcvxCRV, owner=safe.account)
    BVECVX = interface.ISettV4h(r.sett_vaults.bveCVX, owner=safe.account)

    # bcvxcrv to tree to solve deficit
    # NOTE: likely after Q4 maybe this line is not relevant anymore
    BCVXCRV.transfer(r.badger_wallets.badgertree, BCVXCRV.balanceOf(safe))
    # influce token to voter
    BVECVX.transfer(r.badger_wallets.treasury_voter_multisig, BVECVX.balanceOf(safe))

    safe.post_safe_tx()
