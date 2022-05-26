from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.rinkeby.badger_wallets.solo_multisig)
    station = interface.IGasStationExact(
        registry.rinkeby.badger_wallets.gas_station, owner=safe.account
    )

    safe.take_snapshot([])

    # transferOwnership from deployer to safe in console first
    # interface.IGasStationExact('0x747a4c9073B68AE16A29e65f4b95C9bbEa1E19cD', owner=accounts.load()).transferOwnership()
    # station.acceptOwnership({'from': safe.account})

    # address[] calldata addresses
    # uint96[] calldata minBalancesWei
    # uint96[] calldata topUpAmountsWei
    station.setWatchList(
        [
            registry.rinkeby.badger_wallets.ops_executor1,
            registry.rinkeby.badger_wallets.ops_executor3,
            registry.rinkeby.badger_wallets.ops_executor7,
            registry.rinkeby.badger_wallets.ops_executor8,
            registry.rinkeby.badger_wallets.ops_executor12
        ],
        [1e18, 1e18, 1e18, 1e18, 1e18],
        [.1e18, .1e18, .1e18, .1e18, .1e18]
    )
    # safe.account.transfer(station, 2e18)

    safe.print_snapshot()

    safe.post_safe_tx()
