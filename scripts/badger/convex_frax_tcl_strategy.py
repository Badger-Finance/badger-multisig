from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# flag
prod = False


# slippage
COEF = 0.95
DEADLINE = 60 * 60 * 12


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

    # 1. claim rewards
    private_vault.getReward()

    # 2. sell all rewards for DAI via cow
    vault.cow.market_sell(fxs, dai, fxs.balanceOf(vault), deadline=DEADLINE, coef=COEF)
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
