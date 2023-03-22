from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main(safe_address, new_owner=r.badger_wallets.dev_multisig):
    """
    - removes all previous owners
    - adds a new single owner, `new_owner`
    - set threshold to 1
    """
    safe = GreatApeSafe(safe_address)
    gnosis_safe = interface.IGnosisSafe_v1_3_0(safe.address, owner=safe.account)

    gnosis_safe.addOwnerWithThreshold(new_owner, 1)
    owners = remove_owners(gnosis_safe)

    assert len(owners) == 1
    assert owners[0] == new_owner
    assert gnosis_safe.getThreshold() == 1

    safe.post_safe_tx()


def remove_owners(gnosis_safe):
    # recursively remove owners until only last owner remains
    owners = gnosis_safe.getOwners()
    if len(owners) == 1:
        return owners
    gnosis_safe.removeOwner(owners[0], owners[1], 1)
    return remove_owners(gnosis_safe)
