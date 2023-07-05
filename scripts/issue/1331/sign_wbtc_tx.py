from brownie import Contract

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


TRANSACTION_ID = 3


def main():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)
    new_wbtc_dao = techops.contract(r.wbtc.dao_multisig)

    assert not new_wbtc_dao.isConfirmed(TRANSACTION_ID)
    assert new_wbtc_dao.isOwner(techops)

    destination, _, data, _ = new_wbtc_dao.transactions(TRANSACTION_ID)

    print(
        f"confirming tx with id {TRANSACTION_ID} being called on",
        destination,
        Contract(destination).decode_input(data),
    )

    new_wbtc_dao.confirmTransaction(TRANSACTION_ID)

    assert new_wbtc_dao.confirmations(TRANSACTION_ID, techops)

    techops.post_safe_tx()
