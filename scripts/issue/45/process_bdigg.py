from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    """
    withdraw bdigg slp position and withdraw all to digg
    """
    
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_multisig)
    safe.init_sushi()
    
    slp = interface.IUniswapV2Pair(registry.eth.treasury_tokens.slpEthBDigg, owner=safe.account)
    bdigg = interface.ISettV4h(registry.eth.treasury_tokens.bDIGG, owner=safe.account)
    digg = interface.ERC20(registry.eth.treasury_tokens.DIGG)

    safe.take_snapshot(tokens=[slp, bdigg, digg])
    
    safe.sushi.remove_liquidity(False, slp, slp.balanceOf(safe) * 10** slp.decimals())
    bdigg.withdrawAll()
    
    safe.print_snapshot()
    # safe.post_safe_tx()