from brownie import interface
from helpers.addresses import registry as registry_addr

def test_deposit_given_amounts(safe, curve, USDC):
    TOKEN = interface.ICurveLP(registry_addr.eth.treasury_tokens.crv3pool, owner=safe.account)
    DAI = interface.ERC20(registry_addr.eth.treasury_tokens.DAI)
    
    bal_before_usdc = USDC.balanceOf(safe)
    bal_before_dai = DAI.balanceOf(safe)
    
    curve.swap(TOKEN, USDC, DAI, USDC.balanceOf(safe))
    
    assert USDC.balanceOf(safe) < bal_before_usdc
    assert DAI.balanceOf(safe) > bal_before_dai