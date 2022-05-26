from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    station = interface.IGasStationExact(
        registry.eth.badger_wallets.gas_station, owner=safe.account
    )

    labels, addrs, min_bals, min_top_ups = [], [], [], []
    for label, addr in registry.eth.badger_wallets.items():
        min_bal = 2e18
        min_top_up = .1e18
        if not label.startswith('ops_') or 'multisig' in label:
            continue
        if 'executor' in label:
            min_bal = 1e18
        if label == 'ops_botsquad':
            min_bal = 5e18
        if label == 'ops_botsquad_cycle0':
            min_top_up = .5e18
        if label == 'ops_deployer':
            min_bal = 5e18
            min_top_up = .5e18
        labels.append(label)
        addrs.append(addr)
        min_bals.append(min_bal)
        min_top_ups.append(min_top_up)
    import pandas as pd
    print(pd.DataFrame(
        {'addrs': addrs, 'min_bals': min_bals, 'min_top_ups': min_top_ups}, index=labels
    ))

    safe.init_chainlink()
    safe.take_snapshot([safe.chainlink.link])

    station.acceptOwnership()

    # address[] calldata addresses
    # uint96[] calldata minBalancesWei
    # uint96[] calldata topUpAmountsWei
    station.setWatchList(addrs, min_bals, min_top_ups)
    safe.account.transfer(station, 10e18)

    safe.chainlink.register_upkeep('GasStationExact', station, 400_000, 125e18)

    safe.post_safe_tx(call_trace=True)
