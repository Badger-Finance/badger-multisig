from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


VAULT = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
TROPS = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)

xSUSHI = interface.ISushiBar(registry.eth.treasury_tokens.xSUSHI)
SUSHI = TROPS.contract(registry.eth.treasury_tokens.SUSHI)
CVX = TROPS.contract(registry.eth.treasury_tokens.CVX)
BVECVX = interface.ISettV4h(
    registry.eth.treasury_tokens.bveCVX, owner=TROPS.account
)


def transfer_xsushi_to_trops():
    TROPS.take_snapshot(tokens=[xSUSHI])
    xSUSHI.transfer(TROPS, xSUSHI.balanceOf(VAULT), {'from': VAULT.account})
    TROPS.print_snapshot()
    VAULT.post_safe_tx()


def unwrap_xsushi():
    TROPS.take_snapshot(tokens=[xSUSHI, SUSHI])
    xSUSHI.leave(xSUSHI.balanceOf(TROPS), {'from': TROPS.account})
    TROPS.print_snapshot()
    TROPS.post_safe_tx()


def post_orders_to_cowswap():
    TROPS.init_cow()
    TROPS.cow.allow_relayer(SUSHI, SUSHI.balanceOf(TROPS))
    half = int(SUSHI.balanceOf(TROPS) / 2)
    a_tenth = int(SUSHI.balanceOf(TROPS) / 10)
    rest = SUSHI.balanceOf(TROPS) - half - 4 * a_tenth
    assert half + 4 * a_tenth + rest == SUSHI.balanceOf(TROPS)
    TROPS.cow.market_sell(SUSHI, CVX, half, deadline=60*60*24)
    TROPS.cow.market_sell(SUSHI, CVX, a_tenth, deadline=60*60*24*10, coef=.99)
    TROPS.cow.market_sell(SUSHI, CVX, a_tenth, deadline=60*60*24*10, coef=.98)
    TROPS.cow.market_sell(SUSHI, CVX, a_tenth, deadline=60*60*24*10, coef=.97)
    TROPS.cow.market_sell(SUSHI, CVX, a_tenth, deadline=60*60*24*10, coef=.96)
    TROPS.cow.market_sell(SUSHI, CVX, rest, deadline=60*60*24*10, coef=.95)
    TROPS.post_safe_tx()


def lock_cvx():
    TROPS.take_snapshot(tokens=[CVX, BVECVX.address])
    VAULT.take_snapshot(tokens=[CVX, BVECVX.address])

    CVX.approve(BVECVX, CVX.balanceOf(TROPS))
    BVECVX.depositFor(VAULT, CVX.balanceOf(TROPS))

    TROPS.print_snapshot()
    VAULT.print_snapshot()
    TROPS.post_safe_tx()
