from brownie import Contract, interface
from brownie_tokens import MintableForkToken

from helpers.addresses import registry as registry_addr


def test_stable_swap(safe, curve):
    DAI = interface.ERC20(registry_addr.eth.treasury_tokens.DAI)
    # might have to overwrite interface.ERC20 here by forcing from explorer:
    # Contract.from_explorer(registry_addr.eth.treasury_tokens.USDC)
    USDC = MintableForkToken(
        registry_addr.eth.treasury_tokens.USDC, owner=safe.account
    )

    amount = 10_000 * 10**USDC.decimals()
    USDC._mint_for_testing(safe.address, amount)

    bal_before_usdc = USDC.balanceOf(safe)
    print(bal_before_usdc)
    bal_before_dai = DAI.balanceOf(safe)

    curve.swap(USDC, DAI, amount)

    assert USDC.balanceOf(safe) == bal_before_usdc - amount
    assert DAI.balanceOf(safe) > bal_before_dai


def test_factory_swap(safe, curve):
    cvxCRV = MintableForkToken(registry_addr.eth.treasury_tokens.cvxCRV)
    CRV = MintableForkToken(
        registry_addr.eth.treasury_tokens.CRV, owner=safe.account
    )

    amount = 100 * 10**CRV.decimals()
    CRV._mint_for_testing(safe.address, amount)

    bal_before_crv = CRV.balanceOf(safe)
    bal_before_cvxcrv = cvxCRV.balanceOf(safe)

    curve.swap(CRV, cvxCRV, amount)

    assert CRV.balanceOf(safe) == bal_before_crv - amount
    assert cvxCRV.balanceOf(safe) > bal_before_cvxcrv
