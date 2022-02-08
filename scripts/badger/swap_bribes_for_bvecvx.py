"""
swap_bribes_for_bvecvx.py: sell all collected convex and votium bribes for
$bvecvx.
"""

from brownie import ETH_ADDRESS, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


SAFE = GreatApeSafe(registry.eth.badger_wallets.politician_multisig)
CVX = SAFE.contract(registry.eth.treasury_tokens.CVX)
BVECVX = interface.ISettV4h(
    registry.eth.treasury_tokens.bveCVX, owner=SAFE.account
)
TREE = GreatApeSafe(registry.eth.badger_wallets.badgertree)
TECHOPS = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)

WANT_TO_SELL = registry.eth.bribe_tokens_claimable.copy()
WANT_TO_SELL.pop('CVX') # SameBuyAndSellToken
WANT_TO_SELL.pop('SPELL')
WANT_TO_SELL.pop('MTA')
WANT_TO_SELL.pop('NSBT')
WANT_TO_SELL.pop('T') # UnsupportedToken


def multi_approve():
    SAFE.init_cow()
    for _, addr in WANT_TO_SELL.items():
        token = SAFE.contract(addr)
        if token.balanceOf(SAFE) > 0:
            print(_, token.balanceOf(SAFE))
            token.approve(SAFE.cow.vault_relayer, token.balanceOf(SAFE))
    SAFE.post_safe_tx(call_trace=True, replace_nonce=18)


def multi_sell():
    SAFE.init_cow()
    for _, addr in WANT_TO_SELL.items():
        token = SAFE.contract(addr)
        if token.balanceOf(SAFE) > 0:
            SAFE.cow.market_sell(
                token, CVX, token.balanceOf(SAFE), deadline=60*60*4
            )
    SAFE.post_safe_tx()


def limit_sell_spell(cvxspell_rate):
    SAFE.init_cow()
    spell = interface.ERC20(
        registry.eth.bribe_tokens_claimable.SPELL, owner=SAFE.account
    )
    SAFE.cow.limit_sell(
        spell, CVX, spell.balanceOf(SAFE), cvxspell_rate * 1e18, deadline=60*60*12
    )
    SAFE.post_safe_tx()


def swap_bvecvxcvxf_pool():
    SAFE.take_snapshot(tokens=[CVX.address, BVECVX.address] \
        + list(registry['eth']['bribe_tokens_claimable'].values())
    )
    SAFE.init_curve()
    SAFE.curve.swap(CVX, BVECVX, CVX.balanceOf(SAFE))
    SAFE.post_safe_tx()


def lock_cvx():
    TECHOPS.take_snapshot(tokens=[CVX.address, BVECVX.address])
    TREE.take_snapshot(tokens=[CVX.address, BVECVX.address])

    CVX.approve(BVECVX, CVX.balanceOf(TECHOPS), {'from': TECHOPS.address})
    BVECVX.depositFor(TREE, CVX.balanceOf(TECHOPS), {'from': TECHOPS.address})

    TREE.print_snapshot()
    TECHOPS.print_snapshot()

    TECHOPS.post_safe_tx()


def sell_t_on_curve():
    t = interface.ERC20(
        registry.eth.bribe_tokens_claimable.T, owner=SAFE.account
    )
    t_v2_pool = interface.ICurvePoolV2(
        registry.eth.crv_factory_pools.t_eth_f, owner=SAFE.account
    )
    cvx_v2_pool = interface.ICurvePoolV2(
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
