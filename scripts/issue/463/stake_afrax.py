from great_ape_safe import GreatApeSafe
from helpers.addresses import r

FRAX_AMT = 307_373e18
DAY = 86400

vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)

# tokens involved
usdc = vault.contract(r.treasury_tokens.USDC)
usdt = vault.contract(r.treasury_tokens.USDT)
dai = vault.contract(r.treasury_tokens.DAI)
frax = vault.contract(r.treasury_tokens.FRAX)
afrax = vault.contract(r.treasury_tokens.aFRAX)


def create_vault():
    vault.init_convex()
    vault.convex.create_vault(afrax)

    vault.post_safe_tx()


def stake_in_vault():
    vault.take_snapshot(tokens=[usdc, usdt, dai, frax, afrax])

    # swap usdc, usdt and dai to get enought FRAX
    vault.init_curve_v2()
    vault.curve_v2.swap(usdc, frax, usdc.balanceOf(vault))
    vault.curve_v2.swap(usdt, frax, usdc.balanceOf(vault))
    vault.curve_v2.swap(dai, frax, 42_200e18)

    # deposit in aave
    vault.init_aave()
    vault.aave.deposit(frax, FRAX_AMT)

    # deposit in our vault
    vault.init_convex()
    convex_vault = vault.contract(vault.convex.get_vault(afrax))
    vault.convex.stake_lock(convex_vault, afrax.balanceOf(vault), DAY)

    vault.post_safe_tx()
