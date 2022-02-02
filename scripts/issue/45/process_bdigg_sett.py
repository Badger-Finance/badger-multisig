from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

BDIGG_TO_WITHDRAW = 1 # ether

def main():
    """
    withdraw bdigg from sett for digg
    """
    
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_multisig)
    bdigg = interface.ISettV4h(registry.eth.treasury_tokens.bDIGG, owner=safe.account)
    digg = interface.ERC20(registry.eth.treasury_tokens.DIGG)

    safe.take_snapshot(tokens=[bdigg, digg])
    
    bdigg.withdraw(BDIGG_TO_WITHDRAW * 10** bdigg.decimals())
    
    safe.print_snapshot()
    safe.post_safe_tx()