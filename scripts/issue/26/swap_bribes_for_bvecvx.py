"""
swap_bribes_for_bvecvx.py: sell all collected convex and votium bribes for $bvecvx.
"""

from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


SAFE = GreatApeSafe(registry.eth.badger_wallets.politician_multisig)
CVX = SAFE.contract(registry.eth.treasury_tokens.CVX)
BVECVX = SAFE.contract(registry.eth.treasury_tokens.bveCVX)


def multi_approve():
    SAFE.init_cow()
    for _, addr in registry.eth.bribe_tokens_claimable.items():
        token = SAFE.contract(addr)
        if token.balanceOf(SAFE) > 1: #1e18:
            token.approve(SAFE.cow.vault_relayer, token.balanceOf(SAFE))
    SAFE.post_safe_tx(call_trace=True)


def multi_sell():
    SAFE.init_cow()
    for _, addr in registry.eth.bribe_tokens_claimable.items():
        token = SAFE.contract(addr)
        if token.balanceOf(SAFE) > 1e18:
            SAFE.cow.market_sell(token, CVX, token.balanceOf(SAFE))
    SAFE.post_safe_tx()


def limit_sell_spell():
    SAFE.init_cow()
    spell = interface.ERC20(
        registry.eth.bribe_tokens_claimable.SPELL, owner=SAFE.account
    )
    SAFE.cow.limit_sell(
        spell, CVX, spell.balanceOf(SAFE), 6100 * 1e18, deadline=60*60*12
    )
    SAFE.post_safe_tx()


def swap_bvecvxcvxf_pool():
    SAFE.make_safesnap(tokens=[CVX.address, BVECVX.address] \
        + list(registry['eth']['bribe_tokens_claimable'].values())
    )
    SAFE.init_curve()
    SAFE.curve.swap(CVX, BVECVX, CVX.balanceOf(SAFE))
    SAFE.post_safe_tx()
