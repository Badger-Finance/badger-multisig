from great_ape_safe import GreatApeSafe
from helpers.addresses import r

FRAX_AMT = 307_373e18
DAY = 86400

vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)

afrax = vault.contract(r.treasury_tokens.aFRAX)


def create_vault():
    vault.init_convex()
    vault.convex.create_vault(afrax)

    vault.post_safe_tx()


def afrax_sourcing():
    crv3pool = trops.contract(r.treasury_tokens.crv3pool)
    frax = trops.contract(r.treasury_tokens.FRAX)
    dai = trops.contract(r.treasury_tokens.DAI)

    trops.take_snapshot(tokens=[dai, crv3pool])
    vault.take_snapshot(tokens=[afrax])

    # swap 3crv -> frax
    trops.init_curve()
    trops.curve.withdraw_to_one_coin(crv3pool, FRAX_AMT, dai)
    trops.curve.swap(crv3pool, frax, FRAX_AMT)

    # deposit in aave
    trops.init_aave()
    trops.aave.deposit(frax, FRAX_AMT, vault.address)

    vault.print_snapshot()
    trops.post_safe_tx()


def stake_in_vault():
    vault.take_snapshot(tokens=[afrax])

    # deposit in our vault
    vault.init_convex()
    vault.convex.stake_lock(afrax, afrax.balanceOf(vault), DAY)

    vault.post_safe_tx()
