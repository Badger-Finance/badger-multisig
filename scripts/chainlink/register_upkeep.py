'''
ref: https://github.com/smartcontractkit/keeper/blob/master/contracts/UpkeepRegistrationRequests.sol
'''

from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


LINK_MANTISSA = 125e18


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    safe.init_chainlink()

    safe.take_snapshot([safe.chainlink.link])

    safe.chainlink.register_upkeep(
        'GasStationExact',
        registry.eth.drippers.tree_2022_q2,
        400_000,
        125e18
    )

    safe.post_safe_tx(call_trace=True)
