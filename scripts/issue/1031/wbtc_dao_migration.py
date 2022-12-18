from great_ape_safe import GreatApeSafe
from helpers.addresses import r


TRANSACTION_ID = 0


def main():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)
    new_wbtc_dao = techops.contract(r.wbtc.dao_multisig)

    assert not new_wbtc_dao.isConfirmed(TRANSACTION_ID)
    assert new_wbtc_dao.isOwner(techops)

    new_wbtc_dao.confirmTransaction(TRANSACTION_ID)

    assert new_wbtc_dao.confirmations(TRANSACTION_ID, techops)

    techops.post_safe_tx()
