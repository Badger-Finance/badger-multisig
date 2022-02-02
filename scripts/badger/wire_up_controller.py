from brownie import web3

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


# assuming dev_multisig
SAFE = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
SAFE.init_badger()


def wire_up_controller(controller_addr, vault_addr, strat_addr):
    """
    Sets the strategy and vault in a given controller.
    """
    controller_addr = web3.toChecksumAddress(controller_addr)
    vault_addr = web3.toChecksumAddress(vault_addr)
    strat_addr = web3.toChecksumAddress(strat_addr)

    SAFE.badger.wire_up_controller(controller_addr, vault_addr, strat_addr)
    SAFE.post_safe_tx()
