"""
swap_bribes_for_bvecvx.py: sell all collected convex and votium bribes for
$bvecvx and $badger---as per bip87.
"""

from brownie import Contract, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


SAFE = GreatApeSafe(registry.eth.badger_wallets.politician_multisig)
CVX = SAFE.contract(registry.eth.treasury_tokens.CVX)
BVECVX = interface.ISettV4h(
    registry.eth.treasury_tokens.bveCVX, owner=SAFE.account
)
WETH = interface.IWETH9(registry.eth.treasury_tokens.WETH, owner=SAFE.account)
BADGER = interface.ERC20(
    registry.eth.treasury_tokens.BADGER, owner=SAFE.account
)
TREE = GreatApeSafe(registry.eth.badger_wallets.badgertree)
TECHOPS = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
VAULT = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
VOTING_SAFE = GreatApeSafe(registry.eth.badger_wallets.bvecvx_voting_multisig)

WANT_TO_SELL = registry.eth.bribe_tokens_claimable.copy()
WANT_TO_SELL.pop('CVX') # SameBuyAndSellToken

# not enough volume to make gas for swap worth it
WANT_TO_SELL.pop('MTA')
WANT_TO_SELL.pop('NSBT')

# percentage of the bribes that is used to buyback $badger
BADGER_SHARE = .275
# percentage of the bribes that are dedicated to the treasury
OPS_FEE = .05


def multi_approve():
    SAFE.init_cow()
    for symbol, addr in WANT_TO_SELL.items():
        token = SAFE.contract(addr)
        if token.balanceOf(SAFE) > 0:
            print(symbol, token.balanceOf(SAFE))
            token.approve(SAFE.cow.vault_relayer, token.balanceOf(SAFE))
    SAFE.post_safe_tx(call_trace=True)


def multi_sell():
    SAFE.init_cow()
    for _, addr in WANT_TO_SELL.items():
        token = SAFE.contract(addr)
        if token.balanceOf(SAFE) > 0:
            SAFE.cow.market_sell(
                token, CVX, token.balanceOf(SAFE), deadline=60*60*4
            )
    SAFE.post_safe_tx()


def multi_sell_cheap(coef=.985):
    SAFE.init_cow()
    for _, addr in WANT_TO_SELL.items():
        token = SAFE.contract(addr)
        if token.balanceOf(SAFE) > 0:
            SAFE.cow.market_sell(
                token, WETH, token.balanceOf(SAFE), deadline=60*60, coef=coef
            )
    SAFE.post_safe_tx()


def swap_for_cvx_and_badger():
    badger_share = int(WETH.balanceOf(SAFE) * BADGER_SHARE)
    cvx_share = WETH.balanceOf(SAFE) - badger_share
    assert badger_share + cvx_share == WETH.balanceOf(SAFE)
    SAFE.init_cow()
    SAFE.cow.allow_relayer(WETH, WETH.balanceOf(SAFE))
    SAFE.cow.market_sell(
        WETH, BADGER, badger_share, deadline=60*60, coef=.98,
        destination=TREE.address
    )
    SAFE.cow.market_sell(WETH, CVX, cvx_share, deadline=60*60, coef=.98)
    SAFE.post_safe_tx()


def swap_bvecvxcvxf_pool():
    SAFE.take_snapshot(tokens=[CVX.address, BVECVX.address] \
        + list(registry['eth']['bribe_tokens_claimable'].values())
    )
    SAFE.init_curve()
    SAFE.curve.swap(CVX, BVECVX, CVX.balanceOf(SAFE))
    SAFE.post_safe_tx()


def lock_cvx():
    SAFE.take_snapshot(tokens=[CVX.address, BVECVX.address])
    TREE.take_snapshot(tokens=[CVX.address, BVECVX.address])
    VOTING_SAFE.take_snapshot(tokens=[CVX.address, BVECVX.address])

    CVX.approve(BVECVX, CVX.balanceOf(SAFE))
    total = CVX.balanceOf(SAFE)
    ops_fee = int(total / (1 - BADGER_SHARE) * OPS_FEE)
    emissions = total - ops_fee
    assert emissions + ops_fee == CVX.balanceOf(SAFE)
    BVECVX.depositFor(VOTING_SAFE, ops_fee)
    BVECVX.depositFor(TREE, emissions)

    VOTING_SAFE.print_snapshot()
    TREE.print_snapshot()
    SAFE.print_snapshot()

    SAFE.post_safe_tx()


def sell_t_on_curve():
    t = interface.ERC20(
        registry.eth.bribe_tokens_claimable.T, owner=SAFE.account
    )
    t_v2_pool = Contract(
        registry.eth.crv_factory_pools.t_eth_f, owner=SAFE.account
    )
    cvx_v2_pool = Contract(
        registry.eth.crv_factory_pools.cvx_eth_f, owner=SAFE.account
    )
    SAFE.init_curve_v2()
    SAFE.take_snapshot([t.address, CVX.address])

    bal_t = t.balanceOf(SAFE)
    t.approve(t_v2_pool, bal_t)
    i, j = 1, 0
    expected = t_v2_pool.get_dy(i, j, bal_t) * (
        1 - SAFE.curve_v2.max_slippage_and_fees
    )
    t_v2_pool.exchange(i, j, bal_t, expected, True)

    bal_eth = SAFE.account.balance() * .995 # dusty
    i, j = 0, 1
    expected = cvx_v2_pool.get_dy(i, j, bal_eth) * (
        1 - SAFE.curve_v2.max_slippage_and_fees
    )
    cvx_v2_pool.exchange(i, j, bal_eth, expected, True, {'value': bal_eth})

    SAFE.post_safe_tx()
