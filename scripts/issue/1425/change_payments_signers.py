from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console

C = Console()

SENTINEL_OWNERS = "0x0000000000000000000000000000000000000001"

FINAL_STATE = [
    "0x54cF9dF9dCd78E470AB7CB892D7bFbE114c025fc",
    "0x6dd1e005c90cedbea99909fa9ff82497e2424357",
    "0xD10617AE4Da733d79eF0371aa44cd7fa74C41f6B",
    "0x5A6a00d4fCE5DdF1a14868bb27340b542421EDe5",
    "0xaC7B5f4E631b7b5638B9b41d07f1eBED30753f16",
    "0x66496eBB9d848C6A8F19612a6Dd10E09954532D0",
]

FINAL_POLICY = 3


def main():
    safe = GreatApeSafe(r.badger_wallets.payments_multisig)
    payments_multisig = interface.IGnosisSafe_v1_3_0(safe.address, owner=safe.account)

    payments_current = payments_multisig.getOwners()

    unique_to_current = list(set(payments_current).difference(set(FINAL_STATE)))
    unique_to_final = list(set(FINAL_STATE).difference(set(payments_current)))

    # Swap out any unique addresses to ibBTC
    for i in range(len(unique_to_current)):
        C.print(f"Swapping {unique_to_current[i]} for {unique_to_final[i]}...")

        payments_multisig.swapOwner(
            get_previous_owner(payments_multisig, unique_to_current[i]),
            unique_to_current[i],
            unique_to_final[i],
        )

    # Add any missing owners
    payments_current = payments_multisig.getOwners()
    for owner in FINAL_STATE:
        if owner not in payments_current:
            payments_multisig.addOwnerWithThreshold(owner, FINAL_POLICY)

    # Confirm all owners
    for owner in payments_multisig.getOwners():
        assert owner in FINAL_STATE
    assert len(payments_multisig.getOwners()) == len(FINAL_STATE)

    C.print(f"\nNew Owners at payments_multisig Multisig:")
    C.print(f"[green]{payments_multisig.getOwners()}[/green]\n")

    safe.post_safe_tx()


def get_previous_owner(safe, owner):
    owners = safe.getOwners()
    for i in range(len(owners)):
        if owners[i] == owner:
            if i == 0:
                return SENTINEL_OWNERS
            else:
                return owners[i - 1]
