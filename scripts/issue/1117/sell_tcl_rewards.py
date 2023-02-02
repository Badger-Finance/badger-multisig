from great_ape_safe import GreatApeSafe
from helpers.addresses import r


prod = False

COEF = 0.95
DEADLINE = 60 * 60 * 12


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_cow(prod=prod)

    usdc = vault.contract(r.treasury_tokens.USDC)
    dai = vault.contract(r.treasury_tokens.DAI)
    aura = vault.contract(r.treasury_tokens.AURA)
    bal = vault.contract(r.treasury_tokens.BAL)
    crv = vault.contract(r.treasury_tokens.CRV)
    cvx = vault.contract(r.treasury_tokens.CVX)
    fxs = vault.contract(r.treasury_tokens.FXS)

    vault.cow.market_sell(
        aura, usdc, aura.balanceOf(vault), deadline=DEADLINE, coef=COEF
    )

    vault.cow.market_sell(bal, usdc, bal.balanceOf(vault), deadline=DEADLINE, coef=COEF)

    vault.cow.market_sell(fxs, dai, fxs.balanceOf(vault), deadline=DEADLINE, coef=COEF)

    # https://curve.readthedocs.io/exchange-lp-tokens.html#CurveToken.approve
    crv.approve(vault.cow.vault_relayer, 0)

    vault.cow.market_sell(
        crv,
        dai,
        crv.balanceOf(vault),
        deadline=DEADLINE,
        coef=COEF,
    )

    vault.cow.market_sell(
        cvx,
        dai,
        cvx.balanceOf(vault),
        deadline=DEADLINE,
        coef=COEF,
    )

    vault.post_safe_tx()
