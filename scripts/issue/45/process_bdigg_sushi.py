from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


SLP_TO_WITHDRAW = 5 # ether

def main():
    """
    withdraw slp from weth/bdigg position to digg
    """
    
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_multisig)
    safe.init_sushi()
    
    slp = interface.IUniswapV2Pair(registry.eth.treasury_tokens.slpEthBDigg, owner=safe.account)
    bdigg = interface.ISettV4h(registry.eth.treasury_tokens.bDIGG, owner=safe.account)
    digg = interface.ERC20(registry.eth.treasury_tokens.DIGG)
    weth = interface.ERC20(registry.eth.treasury_tokens.WETH, owner=safe.account)
    wbtc = registry.eth.treasury_tokens.WBTC

    safe.take_snapshot(tokens=[slp, bdigg, digg])
    
    bdigg_before = bdigg.balanceOf(safe)
    weth_before = weth.balanceOf(safe)
    safe.sushi.remove_liquidity(False, slp, SLP_TO_WITHDRAW * 10** slp.decimals())
    bdigg.withdraw(bdigg.balanceOf(safe) - bdigg_before)
    safe.sushi.swap_tokens_for_tokens(weth, weth.balanceOf(safe) - weth_before, [weth, wbtc, digg], safe.account)
    
    safe.print_snapshot()
    safe.post_safe_tx()