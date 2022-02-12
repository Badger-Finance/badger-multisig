from brownie import interface
from helpers.addresses import registry as registry_addr
from brownie_tokens import MintableForkToken

def test_stable_swap(safe, curve):
    three_pool = interface.ICurveLP(registry_addr.eth.treasury_tokens.crv3pool)
    DAI = interface.ERC20(registry_addr.eth.treasury_tokens.DAI)
    USDC = MintableForkToken(registry_addr.eth.treasury_tokens.USDC, owner=safe.address)
    
    amount = 10_000 * 10**USDC.decimals()
    USDC._mint_for_testing(safe.address, amount)
    
    bal_before_usdc = USDC.balanceOf(safe)
    bal_before_dai = DAI.balanceOf(safe)
    
    curve.swap(three_pool, USDC, DAI, amount)
    
    assert USDC.balanceOf(safe) == bal_before_usdc - amount
    assert DAI.balanceOf(safe) > bal_before_dai


def test_factory_swap(safe):
    # currently fails, needs interface for factory metapool (int128/uint256 problem)
    
    cvx_crv_f = interface.ICurveLP("0x9D0464996170c6B9e75eED71c68B99dDEDf279e8")
    cvxCRV = MintableForkToken(registry_addr.eth.treasury_tokens.cvxCRV)
    CRV = MintableForkToken(registry_addr.eth.treasury_tokens.CRV, owner=safe.address)

    safe.init_curve_v2()
    
    amount = 100 * 10**CRV.decimals()
    CRV._mint_for_testing(safe.address, amount)
    
    bal_before_crv = CRV.balanceOf(safe)
    bal_before_cvxcrv = cvxCRV.balanceOf(safe)
    
    safe.curve_v2.swap(cvx_crv_f, CRV, cvxCRV, amount)
    
    assert CRV.balanceOf(safe) == bal_before_crv - amount
    assert cvxCRV.balanceOf(safe) > bal_before_cvxcrv