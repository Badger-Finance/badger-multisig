from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# flag
prod = True


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_cow(prod)

    # tokens
    weth = vault.contract(r.treasury_tokens.WETH)
    gravi = vault.contract(r.sett_vaults.graviAURA)
    aura = vault.contract(r.treasury_tokens.AURA)

    # wd from gravi
    gravi.withdrawAll()

    aura_balance = aura.balanceOf(vault)

    # build ladder orders
    leg_amount = aura_balance // 3

    # 7 days
    deadline = 60 * 60 * 24 * 7

    # approve whole aura stack
    vault.cow.allow_relayer(aura, aura_balance)

    # at market
    vault.cow.market_sell(
        asset_sell=aura,
        asset_buy=weth,
        mantissa_sell=leg_amount,
        deadline=deadline,
        coef=0.985,
        destination=r.badger_wallets.treasury_vault_multisig,
    )

    # at 1%
    vault.cow.market_sell(
        asset_sell=aura,
        asset_buy=weth,
        mantissa_sell=leg_amount,
        deadline=deadline,
        coef=1.01,
        destination=r.badger_wallets.treasury_vault_multisig,
    )

    # at 2%
    vault.cow.market_sell(
        asset_sell=aura,
        asset_buy=weth,
        mantissa_sell=leg_amount,
        deadline=deadline,
        coef=1.02,
        destination=r.badger_wallets.treasury_vault_multisig,
    )

    vault.post_safe_tx()
