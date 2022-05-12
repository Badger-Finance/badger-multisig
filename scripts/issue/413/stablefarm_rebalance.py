from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    vault.init_curve()
    vault.init_convex()
    vault.init_aave()
    vault.init_compound()
    vault.init_balancer()

    crv3pool = trops.contract(registry.eth.treasury_tokens.crv3pool)
    crv3eur = vault.contract(registry.eth.treasury_tokens.crv3eur)
    crvfrax = vault.contract(registry.eth.treasury_tokens.crvFRAX)

    usdt = vault.contract(registry.eth.treasury_tokens.USDT)
    usdc = vault.contract(registry.eth.treasury_tokens.USDC)
    dai = vault.contract(registry.eth.treasury_tokens.DAI)
    fei = vault.contract(registry.eth.treasury_tokens.FEI)
    ust = vault.contract(registry.eth.bribe_tokens_claimable.UST)
    frax = vault.contract(registry.eth.treasury_tokens.FRAX)
    eurs = vault.contract(registry.eth.treasury_tokens.EURS)

    ausdc = vault.contract(registry.eth.treasury_tokens.aUSDC)
    ausdt = vault.contract(registry.eth.treasury_tokens.aUSDT)
    afei = vault.contract(registry.eth.treasury_tokens.aFEI)

    cdai = vault.contract(registry.eth.treasury_tokens.cDAI)

    bpt3pool = vault.contract(registry.eth.balancer.B_3POOL)
    bpt3pool_gauge = vault.balancer.gauge_factory.getPoolGauge(bpt3pool)

    trops.take_snapshot(tokens=[crv3pool.address])
    vault.take_snapshot(tokens=[
        crv3pool.address,
        ausdc.address,
        ausdt.address,
        cdai.address,
        afei.address,
        bpt3pool.address,
        bpt3pool_gauge
    ])

    # withdrawals
    crv3pool.transfer(vault, crv3pool.balanceOf(trops))

    vault.convex.unstake_all_and_withdraw_all(crv3pool)
    vault.convex.unstake_all_and_withdraw_all(crv3eur)
    vault.convex.unstake_all_and_withdraw_all(crvfrax)


    vault.curve.withdraw_to_one_coin(crv3eur, crv3eur.balanceOf(vault), eurs)

    vault.curve.swap(eurs, usdc, eurs.balanceOf(vault))
    vault.curve.withdraw_to_one_coin(crvfrax, crvfrax.balanceOf(vault), crv3pool)


    # vault.curve.withdraw_to_one_coin(crv3pool, 614_746e18, usdc)
    vault.curve.withdraw_to_one_coin(crv3pool, 614_746e18, usdt)

    vault.curve.withdraw_to_one_coin(crv3pool, 614_746e18 + 307_373e18, dai)
    vault.curve.swap(dai, fei, 307_373e18, i=1, j=0)

    # deposits
    vault.aave.deposit(usdc, usdc.balanceOf(vault))
    vault.aave.deposit(usdt, usdt.balanceOf(vault))
    vault.aave.deposit(fei, fei.balanceOf(vault))

    vault.compound.deposit(dai, dai.balanceOf(vault))

    vault.curve.withdraw(crv3pool, 307_373e18)
    underlyings = [usdt, usdc, dai]
    amounts = [int(usdt.balanceOf(vault)), int(usdc.balanceOf(vault)), int(dai.balanceOf(vault))]
    vault.balancer.deposit_and_stake(underlyings, amounts)


    # trops.print_snapshot()
    vault.print_snapshot()