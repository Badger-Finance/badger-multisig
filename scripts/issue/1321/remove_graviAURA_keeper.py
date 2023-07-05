from helpers.addresses import r
from great_ape_safe import GreatApeSafe
from helpers.constants import AddressZero

KEEPER = r.keeperAccessControl


def main():
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)
    graviAura = safe.contract(r.sett_vaults.graviAURA)
    assert graviAura.keeper() == KEEPER
    graviAura.setKeeper(AddressZero)
    assert graviAura.keeper() == AddressZero

    safe.post_safe_tx()
