from great_ape_safe import GreatApeSafe
from helpers.addresses import r


SAFE = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
CVX = SAFE.contract(r.treasury_tokens.CVX)
USDC = SAFE.contract(r.treasury_tokens.USDC)
BVECVX = SAFE.contract(r.treasury_tokens.bveCVX)


def main(rebalance=None):
    if rebalance:
        rebalance_pool()
    place_orders()


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
    SAFE.post_safe_tx()


def place_orders():
    SAFE.init_cow()

    leg_amount = CVX.balanceOf(SAFE) // 3
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
