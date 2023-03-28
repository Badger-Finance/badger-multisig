from great_ape_safe import GreatApeSafe
from helpers.addresses import r


prod = False
COEF = 0.98


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    safe.init_badger()
    safe.init_cow(prod=prod)

    bvecvx = safe.contract(r.treasury_tokens.bveCVX)
    cvx = safe.contract(r.treasury_tokens.CVX)
    bcvxcrv = safe.contract(r.treasury_tokens.bcvxCRV)
    cvxcrv = safe.contract(r.treasury_tokens.cvxCRV)
    gravi = safe.contract(r.sett_vaults.graviAURA)
    aura = safe.contract(r.treasury_tokens.AURA)
    aurabal = safe.contract(r.treasury_tokens.AURABAL)
    baurabal = safe.contract(r.sett_vaults.bauraBal)
    xsushi = safe.contract(r.treasury_tokens.xSUSHI)
    usdc = safe.contract(r.treasury_tokens.USDC)

    sell_to_usdc = [cvx, cvxcrv, aura, aurabal, xsushi]

    safe.take_snapshot(tokens=[gravi, bcvxcrv, bvecvx, baurabal])

    safe.badger.claim_all()

    # withdraw so we can sell
    gravi.withdrawAll()
    bcvxcrv.withdrawAll()
    baurabal.withdrawAll()
    bvecvx.withdrawAll()

    for token in sell_to_usdc:
        safe.cow.market_sell(token, usdc, token.balanceOf(safe), 60 * 60 * 4, coef=COEF)

    safe.post_safe_tx()
