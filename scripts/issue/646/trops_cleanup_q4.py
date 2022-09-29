from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
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

    send_to_vault = [cvxcrv, bcvxcrv, baurabal]

    trops.take_snapshot(
        tokens=[bvecvx, bcvxcrv, gravi, usdc, baurabal, cvx] + send_to_vault
    )
    vault.take_snapshot(tokens=send_to_vault)

    # receive bvecvx, bcvxCRV, graviAURA
    trops.badger.claim_all()

    # withdraw all 3crv to usdc
    trops.curve.withdraw_to_one_coin(crv3pool, crv3pool.balanceOf(trops), usdc)

    # deposit cvx
    cvx.approve(bvecvx, cvx.balanceOf(trops))
    bvecvx.deposit(cvx.balanceOf(trops))

    # transfers to vault
    for token in send_to_vault:
        token.transfer(vault, token.balanceOf(trops))

    trops.print_snapshot()
    vault.print_snapshot()
    trops.post_safe_tx()


def sell_to_weth():
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    trops.init_cow(prod=False)

    sd = trops.contract(r.bribe_tokens_claimable_graviaura.SD)
    ens = trops.contract(r.treasury_tokens.ENS)
    sushi = trops.contract(r.treasury_tokens.SUSHI)
    xsushi = trops.contract(r.treasury_tokens.xSUSHI)
    weth = trops.contract(r.treasury_tokens.WETH)

    for token in [sd, ens, sushi, xsushi]:
        trops.cow.market_sell(token, weth, token.balanceOf(trops), deadline=60 * 60 * 4)

    trops.post_safe_tx()
