from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    tree = GreatApeSafe(r.badger_wallets.badgertree)
    trops.init_badger()
    trops.init_curve()

    cvx = trops.contract(r.treasury_tokens.CVX)
    bvecvx = trops.contract(r.treasury_tokens.bveCVX)
    cvxcrv = trops.contract(r.treasury_tokens.cvxCRV)
    bcvxcrv = trops.contract(r.treasury_tokens.bcvxCRV)
    gravi = trops.contract(r.sett_vaults.graviAURA)
    crv3pool = trops.contract(r.treasury_tokens.crv3pool)
    usdc = trops.contract(r.treasury_tokens.USDC)
    baurabal = trops.contract(r.sett_vaults.bauraBal)

    trops.take_snapshot(
        tokens=[bvecvx, cvxcrv, gravi, usdc, baurabal, cvx, baurabal]
    )
    vault.take_snapshot(tokens=[baurabal])
    voter.take_snapshot(tokens=[bvecvx])
    tree.take_snapshot(tokens=[bcvxcrv])

    # receive bvecvx, bcvxCRV, graviAURA
    trops.badger.claim_all()

    # withdraw all 3crv to usdc
    trops.curve.withdraw_to_one_coin(crv3pool, crv3pool.balanceOf(trops), usdc)

    # deposit cvx for voter
    cvx.approve(bvecvx, cvx.balanceOf(trops))
    bvecvx.depositFor(voter, cvx.balanceOf(trops))

    # deposit cvxcrv for tree
    cvxcrv.approve(bcvxcrv, cvxcrv.balanceOf(trops))
    bcvxcrv.depositFor(tree, cvxcrv.balanceOf(trops))
    bcvxcrv.transfer(tree, bcvxcrv.balanceOf(trops))

    # transfers to vault
    baurabal.transfer(vault, baurabal.balanceOf(trops))

    trops.print_snapshot()
    vault.print_snapshot()
    voter.print_snapshot()
    tree.print_snapshot()
    trops.post_safe_tx()


def sell_to_weth():
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    trops.init_cow(prod=False)

    sd = trops.contract(r.bribe_tokens_claimable_graviaura.SD)
    dfx = trops.contract(r.bribe_tokens_claimable_graviaura.DFX)
    rpl = trops.contract(r.bribe_tokens_claimable_graviaura.RPL)
    ens = trops.contract(r.treasury_tokens.ENS)
    sushi = trops.contract(r.treasury_tokens.SUSHI)
    xsushi = trops.contract(r.treasury_tokens.xSUSHI)
    weth = trops.contract(r.treasury_tokens.WETH)

    for token in [sd, ens, dfx, rpl, sushi, xsushi]:
        trops.cow.market_sell(token, weth, token.balanceOf(trops), deadline=60 * 60 * 4)

    trops.post_safe_tx()
