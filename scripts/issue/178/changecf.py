from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from rich.console import Console


console = Console()

COLLATERAL_FACTOR = 0.85


def main():
    """
    change collateral factor of fdola from 0.75 to 0.85
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_rari()

    fdola = registry.eth.rari['fDOLA-22']

    fdola_cf_before = safe.rari.ftoken_get_cf(fdola)
    safe.rari.ftoken_set_cf(fdola, COLLATERAL_FACTOR)
    fdola_cf_after = safe.rari.ftoken_get_cf(fdola)

    console.print("fDOLA collateral factor before:", fdola_cf_before)
    console.print("fDOLA collateral factor after:", fdola_cf_after)

    safe.post_safe_tx()
