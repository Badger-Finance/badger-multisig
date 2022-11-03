from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.techops_multisig)
    safe.init_badger()
    safe.badger.set_gas_station_watchlist()
    safe.post_safe_tx(call_trace=True)
