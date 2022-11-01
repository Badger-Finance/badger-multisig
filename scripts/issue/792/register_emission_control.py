from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import chain

contract_registry = registry()
chain_safe = GreatApeSafe(contract_registry.badger_wallets.techops_multisig)
chain_safe.init_badger()

def get_emission_control():
    if chain.id == 1:
        return '0x31825c0a6278b89338970e3eb979b05b27faa263'
    elif chain.id == 42161:
        return '0x78418681f9ed228d627f785fb9607ed5175518fd'
    else:
        raise Exception('Invalid chain')

def main():
    chain_safe.badger.set_key_on_registry('emissionControl', get_emission_control())
    chain_safe.post_safe_tx()
