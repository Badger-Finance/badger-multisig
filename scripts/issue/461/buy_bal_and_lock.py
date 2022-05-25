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
    voter.post_safe_tx()


def swap_bvecvx():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    trops.init_curve()

    bvecvx = trops.contract(registry.eth.treasury_tokens.bveCVX)
    cvx = trops.contract(registry.eth.treasury_tokens.CVX)

    trops.take_snapshot(tokens=[bvecvx, cvx])

    trops.curve.swap(bvecvx, cvx, 25_000e18)

    trops.print_snapshot()
    trops.post_safe_tx()


def post_cvx_orders():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    trops.init_cow()

    cvx = trops.contract(registry.eth.treasury_tokens.CVX)
    bal = trops.contract(registry.eth.treasury_tokens.BAL)

    amount = 25_000e18
    trops.cow.allow_relayer(cvx, cvx.balanceOf(trops))
    half = int(amount / 2)
    a_tenth = int(amount / 10)
    rest = amount - half - 4 * a_tenth
    trops.cow.market_sell(cvx, bal, half, deadline=60*60*24)
    trops.cow.market_sell(cvx, bal, a_tenth, deadline=60*60*24*10, coef=1.03)
    trops.cow.market_sell(cvx, bal, a_tenth, deadline=60*60*24*10, coef=1.06)
    trops.cow.market_sell(cvx, bal, a_tenth, deadline=60*60*24*10, coef=1.09)
    trops.cow.market_sell(cvx, bal, a_tenth, deadline=60*60*24*10, coef=1.12)
    trops.cow.market_sell(cvx, bal, rest, deadline=60*60*24*10, coef=1.15)
    trops.post_safe_tx()


def transfer_and_lock_bal(simulation="False"):
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    vault.init_balancer()

    if simulation == "True":
        bal = MintableForkToken(
            registry.eth.treasury_tokens.BAL, owner=trops.account
        )
        bal._mint_for_testing(trops, 1000 * 10**bal.decimals())
    else:
        bal = trops.contract(registry.eth.treasury_tokens.BAL)

    vebal = vault.contract(registry.eth.balancer.veBAL)
    weth = vault.contract(registry.eth.treasury_tokens.WETH)

    trops.take_snapshot(tokens=[bal])
    vault.take_snapshot(tokens=[vebal, weth, bal.address])

    bal.transfer(vault, bal.balanceOf(trops))

    bal = vault.contract(registry.eth.treasury_tokens.BAL)

    vault.balancer.lock_bal(mantissa_bal=bal.balanceOf(vault))

    trops.print_snapshot()
    vault.print_snapshot()

