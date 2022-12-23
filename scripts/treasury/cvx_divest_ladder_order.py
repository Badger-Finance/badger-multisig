from decimal import Decimal

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


SAFE = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
CVX = SAFE.contract(r.treasury_tokens.CVX)
USDC = SAFE.contract(r.treasury_tokens.USDC)
BVECVX = SAFE.contract(r.treasury_tokens.bveCVX)
BVECVXCVX = SAFE.contract(r.treasury_tokens.bveCVX_CVX_f)
BBVECVXCVX = SAFE.contract(r.sett_vaults.bbveCVX_CVX_f)


def main(spot_mantissa=0, rebalance=None):
    if rebalance:
        rebalance_pool()
    dogfood()

    SAFE.init_cow()
    SAFE.cow.allow_relayer(CVX, CVX.balanceOf(SAFE))
    place_orders(Decimal(spot_mantissa))


def rebalance_pool():
    pool = SAFE.contract(r.treasury_tokens.bveCVX_CVX_f)
    pool_bve = BVECVX.balanceOf(pool)
    pool_cvx = CVX.balanceOf(pool)
    safe_cvx = CVX.balanceOf(SAFE)
    deficit = pool_bve - pool_cvx
    topup = min(safe_cvx, deficit)
    if topup > 0:
        SAFE.init_curve()
        SAFE.curve.deposit(pool, topup, CVX)
    assert BVECVX.balanceOf(pool) == CVX.balanceOf(pool)


def dogfood():
    # dogfood any crv_bvecvxcvx lp tokens present in the voter msig
    bal_crvlp = BVECVXCVX.balanceOf(SAFE)
    if bal_crvlp > 0:
        BVECVXCVX.approve(BBVECVXCVX, bal_crvlp)
        BBVECVXCVX.depositAll()


def place_orders(spot_mantissa):
    # sell remaining cvx from previous ladder orders that did not fill
    SAFE.cow.market_sell(
        asset_sell=CVX,
        asset_buy=USDC,
        mantissa_sell=spot_mantissa,
        # deadline=, # NOTE: default deadline!
        coef=0.95,
        destination=r.badger_wallets.treasury_vault_multisig,
    )

    # build ladder orders
    leg_amount = (CVX.balanceOf(SAFE) - spot_mantissa) // 3
    deadline = 60 * 60 * 24 * 6  # gives one day to sell at spot before next round

    SAFE.cow.market_sell(
        asset_sell=CVX,
        asset_buy=USDC,
        mantissa_sell=leg_amount,
        deadline=deadline,
        coef=1.05,
        destination=r.badger_wallets.treasury_vault_multisig,
    )
    SAFE.cow.market_sell(
        asset_sell=CVX,
        asset_buy=USDC,
        mantissa_sell=leg_amount,
        deadline=deadline,
        coef=1.075,
        destination=r.badger_wallets.treasury_vault_multisig,
    )
    SAFE.cow.market_sell(
        asset_sell=CVX,
        asset_buy=USDC,
        mantissa_sell=leg_amount,
        deadline=deadline,
        coef=1.1,
        destination=r.badger_wallets.treasury_vault_multisig,
    )

    SAFE.post_safe_tx()
