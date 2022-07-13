from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import Contract, interface
from helpers.constants import AddressZero

"""
  Sets Bribes Processor to target address
"""

def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_badger()

    bve_aura = safe.badger.strat_bve_aura
    tech_ops = registry.eth.badger_wallets.techops_multisig

    aura_bribes_processor = interface.IBribesProcessor(registry.eth.aura_bribes_processor)

    ## Ensure Strategy makes sense
    assert aura_bribes_processor.STRATEGY() == bve_aura

    ## Ensure delegation has happened (for security reasons)
    assert aura_bribes_processor.manager() == tech_ops

    ## Because it's setup let's make sure no address was set previously
    assert aura_bribes_processor.bribesProcessor() == AddressZero

    ## Set it up
    bve_aura.setBribesProcessor(aura_bribes_processor)

    assert aura_bribes_processor.bribesProcessor() == aura_bribes_processor

