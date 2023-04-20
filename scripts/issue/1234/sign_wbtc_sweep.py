from brownie import Contract

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


TRANSACTION_ID = [1, 2]


def main():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)
    new_wbtc_dao = techops.contract(r.wbtc.dao_multisig)

    for tid in TRANSACTION_ID:
        assert not new_wbtc_dao.isConfirmed(tid)
        assert new_wbtc_dao.isOwner(techops)

        destination, _, data, _ = new_wbtc_dao.transactions(tid)

        print(
            f"confirming tx with id {tid} being called on",
            destination,
            Contract(destination).decode_input(data),
        )

        new_wbtc_dao.confirmTransaction(tid)

        assert new_wbtc_dao.confirmations(tid, techops)

    techops.post_safe_tx()
