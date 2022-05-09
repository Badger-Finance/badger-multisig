from brownie import accounts, chain, interface, web3
from web3.middleware import geth_poa_middleware

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


SAFE = GreatApeSafe(registry.rinkeby.badger_wallets.solo_multisig)
STATION = interface.IGasStation(registry.rinkeby.badger_wallets.gas_station)


def renounce_deployer():
    if chain.id == 4:
        # https://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    STATION.transferOwnership(SAFE, {'from': accounts.load('badger_deployer8')})


def main():
    SAFE.take_snapshot([])

    STATION.acceptOwnership({'from': SAFE.account})

    # address[] calldata addresses
    # uint96[] calldata minBalancesWei
    # uint96[] calldata topUpAmountsWei
    STATION.setWatchList(
        [
            registry.rinkeby.badger_wallets.ops_executor1,
            registry.rinkeby.badger_wallets.ops_executor7,
            registry.rinkeby.badger_wallets.ops_executor8,
            registry.rinkeby.badger_wallets.ops_executor12
        ],
        [1e18, 1e18, 1e18, 1e18],
        [.1e18, .1e18, .1e18, .1e18],
        {'from': SAFE.account}
    )
    SAFE.account.transfer(STATION, 5e18)

    SAFE.print_snapshot()

    SAFE.post_safe_tx()
