from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# flag
prod = False


# slippage
COEF = 0.98


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_cow(prod)

    # tokens involved
    dai = vault.contract(r.treasury_tokens.DAI)
    fxs = vault.contract(r.treasury_tokens.FXS)
    crv = vault.contract(r.treasury_tokens.CRV)
    cvx = vault.contract(r.treasury_tokens.CVX)

    # contracts
    private_vault = vault.contract(r.convex.frax.private_vaults.badger_fraxbp)

    # snap
    tokens = [fxs, crv, cvx]
    vault.take_snapshot(tokens)

    # NOTE: vault contains crv & cvx > 0, to make sure it is only the strat rewards check balances before
    crv_balance_before = crv.balanceOf(vault)
    cvx_balance_before = cvx.balanceOf(vault)

    # 1. claim rewards
    private_vault.getReward()

    # 2. sell all rewards for DAI via cow
    vault.cow.market_sell(
        fxs, dai, fxs.balanceOf(vault), deadline=60 * 60 * 4, coef=COEF
    )
    vault.cow.market_sell(
        crv,
        dai,
        crv.balanceOf(vault) - crv_balance_before,
        deadline=60 * 60 * 4,
        coef=COEF,
    )
    vault.cow.market_sell(
        cvx,
        dai,
        cvx.balanceOf(vault) - cvx_balance_before,
        deadline=60 * 60 * 4,
        coef=COEF,
    )

    vault.post_safe_tx()
