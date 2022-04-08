
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface
from eth_abi import encode_abi


def main(ftoken_addr):
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_rari()

    safe.rari.ftoken_pause(ftoken_addr, rf=0)

    if safe.rari.ftoken_get_admin_fee != 0:
        safe.rari.ftoken_set_admin_fee(ftoken_addr, 0)

    safe.post_safe_tx()
