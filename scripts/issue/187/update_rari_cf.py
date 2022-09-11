from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import Contract
from rich.console import Console

console = Console()

COLLATERAL_FACTOR = 0.85


def main():
    """
    change collateral factor for remaining stables to 85%
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_rari()

    f_names = ["fUSDC-22", "fDAI-22", "fFEI-22", "fFRAX-22"]  # DOLA already at 85%
    f_addrs = dict(registry.eth.rari.items())

    f_stables = [Contract(f_addrs[name]) for name in f_names]

    ftoken_cfs = {}
    for ftoken in f_stables:
        safe.rari.ftoken_set_cf(ftoken, COLLATERAL_FACTOR)
        new_cf = safe.rari.ftoken_get_cf(ftoken)
        ftoken_cfs[ftoken.symbol()] = new_cf

    console.print("New CFs:")
    console.print(ftoken_cfs)

    safe.post_safe_tx()
