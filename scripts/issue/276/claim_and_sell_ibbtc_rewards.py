from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# slippages
COEF = 0.93
DEADLINE = 60 * 60 * 24


def main():
    safe = GreatApeSafe(r.badger_wallets.ibbtc_multisig)
    safe.init_badger()
    safe.init_cow(prod=True)

    # Tokens
    badger = safe.contract(r.treasury_tokens.BADGER)
    cvx = safe.contract(r.treasury_tokens.CVX)
    cvxCrv = safe.contract(r.treasury_tokens.cvxCRV)
    weth = safe.contract(r.treasury_tokens.WETH)

    # Vaults
    bveCVX = safe.contract(r.sett_vaults.bveCVX)
    bcvxCRV = safe.contract(r.sett_vaults.bcvxCRV)

    # Take snapshot
    safe.take_snapshot([badger, cvx, cvxCrv, bveCVX, bcvxCRV, weth])

    # Claim all rewards from Tree
    safe.badger.claim_all()

    # Withdraw from vaults
    if bveCVX.balanceOf(safe) > 0:
        bveCVX.withdrawAll()

    if bcvxCRV.balanceOf(safe) > 0:
        bcvxCRV.withdrawAll()

    # Sell all CVX and cvxCRV
    cvx_balance = cvx.balanceOf(safe)
    if cvx_balance > 0:
        safe.cow.market_sell(cvx, weth, cvx_balance, deadline=DEADLINE, coef=COEF)

    cvxCrv_balance = cvxCrv.balanceOf(safe)
    if cvxCrv_balance > 0:
        safe.cow.market_sell(cvxCrv, weth, cvxCrv_balance, deadline=DEADLINE, coef=COEF)

    safe.print_snapshot()
    safe.post_safe_tx()
