from numpy import transpose
from regex import W
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie_tokens import MintableForkToken


def transfer_bvecvx():
    voter = GreatApeSafe(registry.eth.badger_wallets.bvecvx_voting_multisig)
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)

    bvecvx = voter.contract(registry.eth.treasury_tokens.bveCVX)

    voter.take_snapshot(tokens=[bvecvx])
    trops.take_snapshot(tokens=[bvecvx])

    bvecvx.transfer(trops, 25_000e18)

    voter.print_snapshot()
    trops.print_snapshot()
    # voter.post_safe_tx()


def swap_bvecvx():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    trops.init_curve()

    bvecvx = trops.contract(registry.eth.treasury_tokens.bveCVX)
    cvx = trops.contract(registry.eth.treasury_tokens.CVX)

    trops.take_snapshot(tokens=[bvecvx, cvx])

    trops.curve.swap(bvecvx, cvx, 25_000e18)

    trops.print_snapshot()
    # trops.post_safe_tx()


def post_cvx_orders():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    trops.init_cow()

    cvx = trops.contract(registry.eth.treasury_tokens.CVX)
    bal = trops.contract(registry.eth.treasury_tokens.BAL)

    trops.cow.allow_relayer(cvx, cvx.balanceOf(trops))
    half = int(cvx.balanceOf(trops) / 2)
    # floor?
    a_tenth = int(half / 5)
    trops.cow.market_sell(cvx, bal, half, deadline=60*60*24)
    trops.cow.market_sell(cvx, bal, a_tenth, deadline=60*60*24*10, coef=1.03)
    trops.cow.market_sell(cvx, bal, a_tenth, deadline=60*60*24*10, coef=1.06)
    trops.cow.market_sell(cvx, bal, a_tenth, deadline=60*60*24*10, coef=1.09)
    trops.cow.market_sell(cvx, bal, a_tenth, deadline=60*60*24*10, coef=1.12)
    trops.cow.market_sell(cvx, bal, a_tenth, deadline=60*60*24*10, coef=1.15)
    trops.post_safe_tx()


def transfer_and_lock_bal():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    vault.init_balancer()

    bal = trops.contract(registry.eth.treasury_tokens.BAL)
    weth = vault.contract(registry.eth.treasury_tokens.WETH)
    bpt = vault.contract(registry.eth.balancer.B_80_BAL_20_WETH)


    trops.take_snapshot(tokens=[bal])
    vault.take_snapshot(tokens=[bal, weth])

    bal.transfer(vault, bal.balanceOf(trops))

    # trops.print_snapshot()
    # vault.print_snapshot()

    bal = vault.contract(registry.eth.treasury_tokens.BAL)
    vault.balancer.swap_and_lock_bal(bal.balanceOf(vault))

    vault.print_snapshot()


def main():
    transfer_bvecvx()
    swap_bvecvx()
