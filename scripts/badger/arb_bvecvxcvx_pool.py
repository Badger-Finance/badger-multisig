from brownie import interface
from sympy import Symbol
from sympy.solvers import solve

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


TARGET = .55
THRESHOLD = 5000


def main():
    """
    arbitrage the bvecvxcvx factory pool. if bvecvx dominance is < TARGET, calc
    how much bvecvx exactly should be added to reach TARGET. make sure that
    the to be added bvecvx > THRESHOLD.
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    safe.init_curve()

    cvx = interface.ERC20(registry.eth.treasury_tokens.CVX, owner=safe.account)
    bvecvx = interface.ISettV4h(
        registry.eth.treasury_tokens.bveCVX, owner=safe.account
    )
    bvecvxcvx = interface.IStableSwap2Pool(
        registry.eth.treasury_tokens['bveCVX-CVX-f'], owner=safe.account
    )

    safe.take_snapshot(tokens=[bvecvx.address, bvecvxcvx.address])

    bal_cvx = cvx.balanceOf(bvecvxcvx)
    bal_bvecvx = bvecvx.balanceOf(bvecvxcvx)
    bal_total = bal_cvx + bal_bvecvx # TODO: take ppfs (now==1) into account
    cvx_dominance = bal_cvx / bal_total
    bvecvx_dominance = bal_bvecvx / bal_total
    print('cvx\t\t', bal_cvx / 1e18, cvx_dominance)
    print('bvecvx\t\t', bal_bvecvx / 1e18, bvecvx_dominance)
    print('cvx+bvecvx\t', bal_total / 1e18)

    if bvecvx_dominance < TARGET:
        x = Symbol('x')
        mantissa_to_add = solve(
            (int(bal_bvecvx) + x) / (int(bal_total) + x) - TARGET, x
        )[0]
        if mantissa_to_add >= bvecvx.balanceOf(safe):
            mantissa_to_add = bvecvx.balanceOf(safe)
        assert mantissa_to_add > THRESHOLD * 1e18
        safe.curve.deposit(bvecvxcvx, mantissa_to_add, bvecvx)

    bal_cvx = cvx.balanceOf(bvecvxcvx)
    bal_bvecvx = bvecvx.balanceOf(bvecvxcvx)
    bal_total = bal_cvx + bal_bvecvx # TODO: take ppfs (now==1) into account
    cvx_dominance = bal_cvx / bal_total
    bvecvx_dominance = bal_bvecvx / bal_total
    print('cvx\t\t', bal_cvx / 1e18, cvx_dominance)
    print('bvecvx\t\t', bal_bvecvx / 1e18, bvecvx_dominance)
    print('cvx+bvecvx\t', bal_total / 1e18)

    assert bvecvx_dominance <= TARGET

    safe.post_safe_tx()
