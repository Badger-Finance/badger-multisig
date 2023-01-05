from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main(
    upkeep_id=14270489937535892760600590423564455802049459622872924518248134412357549386527,
    gas_limit=1600000,
):
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)

    cl_registry = techops.contract(r.chainlink.keeper_registry)

    cl.registry.setUpkeepGasLimit(int(upkeep_id), int(gas_limit))

    techops.post_safe_tx()
