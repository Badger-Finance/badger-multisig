from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import Contract, interface


VAULT = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
TROPS = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)

xSUSHI = Contract(registry.eth.treasury_tokens.xSUSHI)
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


def market_sell_sushi(amount_eth):
    TROPS.init_cow()
    amount = amount_eth * 10 ** SUSHI.decimals()
    SUSHI.approve(TROPS, amount)
    TROPS.cow.market_sell(SUSHI, CVX, amount)
    TROPS.post_safe_tx()


def lock_cvx():
    TROPS.take_snapshot(tokens=[CVX, BVECVX.address])
    VAULT.take_snapshot(tokens=[CVX, BVECVX.address])

    CVX.approve(BVECVX, CVX.balanceOf(TROPS))
    BVECVX.depositFor(VAULT, CVX.balanceOf(TROPS))

    TROPS.print_snapshot()
    VAULT.print_snapshot()
    TROPS.post_safe_tx()
