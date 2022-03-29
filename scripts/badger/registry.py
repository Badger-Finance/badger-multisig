from brownie import web3
from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


console = Console()

# assuming techOps
SAFE = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
SAFE.init_badger()

def set_key(key, target_addr):
    """
    Sets the input target address on the registry under the specified 'key' 
    """

    SAFE.badger.set_key_on_registry(key, target_addr)
    SAFE.post_safe_tx()
