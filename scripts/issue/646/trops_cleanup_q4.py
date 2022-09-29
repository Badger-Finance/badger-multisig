from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    safe.init_badger()
    safe.init_curve()
    safe.init_cow()

    cvx = safe.contract(r.treasury_tokens.CVX)
    bvecvx = safe.contract(r.treasury_tokens.bveCVX)
    cvxcrv = safe.contract(r.treasury_tokens.cvxCRV)
    bcvxcrv = safe.contract(r.treasury_tokens.bcvxCRV)
    gravi = safe.contract(r.sett_vaults.graviAURA)
    crv3pool = safe.contract(r.treasury_tokens.crv3pool)
    usdc = safe.contract(r.treasury_tokens.USDC)
    baurabal = safe.contract(r.sett_vaults.bauraBal)

    send_to_vault = [cvxcrv, bcvxcrv, baurabal]

    safe.take_snapshot(
        tokens=[bvecvx, bcvxcrv, gravi, usdc, baurabal, cvx] + send_to_vault
    )
    vault.take_snapshot(tokens=send_to_vault)

    # receive bvecvx, bcvxCRV, graviAURA
    safe.badger.claim_all()

    # withdraw all 3crv to usdc
    safe.curve.withdraw_to_one_coin(crv3pool, crv3pool.balanceOf(safe), usdc)

    # deposit cvx
    cvx.approve(bvecvx, cvx.balanceOf(safe))
    bvecvx.deposit(cvx.balanceOf(safe))

    # transfers to vault
    for token in send_to_vault:
        token.transfer(vault, token.balanceOf(safe))

    safe.print_snapshot()
    vault.print_snapshot()
    safe.post_safe_tx()


def sell_to_weth():
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    safe.init_cow(prod=False)

    sd = safe.contract(r.bribe_tokens_claimable_graviaura.SD)
    ens = safe.contract(r.treasury_tokens.ENS)
    sushi = safe.contract(r.treasury_tokens.SUSHI)
    xsushi = safe.contract(r.treasury_tokens.xSUSHI)
    weth = safe.contract(r.treasury_tokens.WETH)

    for token in [sd, ens, sushi, xsushi]:
        safe.cow.market_sell(token, weth, token.balanceOf(safe), deadline=60 * 60 * 4)

    safe.post_safe_tx()
