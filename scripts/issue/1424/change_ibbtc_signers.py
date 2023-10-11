from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console

C = Console()

SENTINEL_OWNERS = "0x0000000000000000000000000000000000000001"


def main():
    safe = GreatApeSafe(r.badger_wallets.ibbtc_multisig)
    ibbtc_multisig = interface.IGnosisSafe_v1_3_0(safe.address, owner=safe.account)
    trops_multisig = interface.IGnosisSafe_v1_3_0(
        r.badger_wallets.treasury_ops_multisig
    )

    trops_owners = trops_multisig.getOwners()
    ibbtc_owners = ibbtc_multisig.getOwners()

    unique_to_ibbtc = list(set(ibbtc_owners).difference(set(trops_owners)))
    unique_to_trops = list(set(trops_owners).difference(set(ibbtc_owners)))

    # Swap out any unique addresses to ibBTC
    for i in range(len(unique_to_ibbtc)):
        C.print(f"Swapping {unique_to_ibbtc[i]} for {unique_to_trops[i]}...")

        ibbtc_multisig.swapOwner(
            get_previous_owner(ibbtc_multisig, unique_to_ibbtc[i]),
            unique_to_ibbtc[i],
            unique_to_trops[i],
        )

    # Add any missing owners
    ibbtc_owners = ibbtc_multisig.getOwners()
    for owner in trops_owners:
        if owner not in ibbtc_owners:
            ibbtc_multisig.addOwnerWithThreshold(owner, 3)

    # Confirm all owners
    for owner in ibbtc_multisig.getOwners():
        assert owner in trops_owners
    assert len(ibbtc_multisig.getOwners()) == len(trops_owners)

    C.print(f"\nNew Owners at ibbtc_multisig Multisig:")
    C.print(f"[green]{ibbtc_multisig.getOwners()}[/green]\n")

    safe.post_safe_tx()


def get_previous_owner(safe, owner):
    owners = safe.getOwners()
    for i in range(len(owners)):
        if owners[i] == owner:
            if i == 0:
                return SENTINEL_OWNERS
            else:
                return owners[i - 1]
