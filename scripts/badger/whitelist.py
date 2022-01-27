from brownie import web3

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


# assuming dev_multisig
SAFE = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
SAFE.init_badger()


def all_setts(candidate_addr):
    """
    Loop over all of Badger's sett vaults, and try to set whitelist
    the address `candidate` to interact with it. In case of timelock being the
    governor, queue the approval through the timelock.
    """
    candidate_addr = web3.toChecksumAddress(candidate_addr)

    for sett_name, sett_addr in registry.eth.sett_vaults.items():
        SAFE.badger.whitelist(candidate_addr, sett_addr, sett_name)
    SAFE.post_safe_tx()


def single_sett(candidate_addr, sett_addr):
    """
    Whitelist `candidate` address on Badger's sett vault `sett_addr`. In
    case of timelock being the governor, queue the approval through the
    timelock.
    """
    candidate_addr = web3.toChecksumAddress(candidate_addr)
    sett_addr = web3.toChecksumAddress(sett_addr)

    SAFE.badger.whitelist(candidate_addr, sett_addr)
    SAFE.post_safe_tx()
