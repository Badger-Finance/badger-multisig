from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface


DUSTY = 0.99


def send_3pool_to_vault():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    crv3pool = trops.contract(registry.eth.treasury_tokens.crv3pool)

    trops.take_snapshot(tokens=[crv3pool.address])
    vault.take_snapshot(tokens=[crv3pool.address])

    crv3pool.transfer(vault, crv3pool.balanceOf(trops))

    trops.post_safe_tx()


def main():
    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    vault.init_curve()
    vault.init_convex()
    vault.init_aave()
    vault.init_compound()
    vault.init_balancer()

    balance_checker = interface.IBalanceChecker(registry.eth.helpers.balance_checker, owner=vault.account)

    usdt = vault.contract(registry.eth.treasury_tokens.USDT)
    usdc = vault.contract(registry.eth.treasury_tokens.USDC)
    dai = vault.contract(registry.eth.treasury_tokens.DAI)
    fei = vault.contract(registry.eth.treasury_tokens.FEI)
    eurs = vault.contract(registry.eth.treasury_tokens.EURS)

    crv3pool = vault.contract(registry.eth.treasury_tokens.crv3pool)
    crv3eur = vault.contract(registry.eth.treasury_tokens.crv3eur)
    crvfrax = vault.contract(registry.eth.treasury_tokens.crvFRAX)

    ausdc = vault.contract(registry.eth.treasury_tokens.aUSDC)
    ausdt = vault.contract(registry.eth.treasury_tokens.aUSDT)
    afei = vault.contract(registry.eth.treasury_tokens.aFEI)

    cdai = vault.contract(registry.eth.treasury_tokens.cDAI)

    bpt3pool = vault.contract(registry.eth.balancer.B_3POOL)
    bpt3pool_gauge = vault.balancer.gauge_factory.getPoolGauge(bpt3pool)

    tokens=[
        crv3pool.address,
        ausdc.address,
        ausdt.address,
        cdai.address,
        afei.address,
        bpt3pool.address,
        bpt3pool_gauge
    ]

    vault.take_snapshot(tokens)

    min_amounts = {
        ausdc: 600_000e18,
        ausdc: 600_000e6,
        ausdt: 600_000e6,
        cdai: 27_000e8,
        afei: 300_000e18,
        bpt3pool_gauge: 300_000e18
    }

    # withdrawals
    vault.convex.unstake_all_and_withdraw_all(crv3pool)
    vault.convex.unstake_all_and_withdraw_all(crv3eur)
    vault.convex.unstake_all_and_withdraw_all(crvfrax)

    vault.curve.withdraw_to_one_coin(crv3eur, crv3eur.balanceOf(vault), eurs)
    vault.curve.withdraw_to_one_coin(crvfrax, crvfrax.balanceOf(vault), crv3pool)
    vault.curve.withdraw_to_one_coin(crv3pool, (614_746e18 + 307_373e18), dai)

    vault.curve.swap(dai, fei, 307_373e18 * 1.005, i=1, j=0)
    vault.curve.swap(eurs, usdc, eurs.balanceOf(vault))

    vault.curve.withdraw_to_one_coin(crv3pool, (614_746e6 - usdc.balanceOf(vault) * DUSTY) * 1e12, usdc)
    vault.curve.withdraw_to_one_coin(crv3pool, 614_746e18, usdt)

    # deposits
    vault.aave.deposit(usdc, 614_746e6)
    vault.aave.deposit(usdt, 614_746e6)
    vault.aave.deposit(fei, 307_373e18)

    vault.compound.deposit(dai, 614_746e18)

    vault.curve.withdraw(crv3pool, 307_373e18)
    underlyings = [usdt, usdc, dai]
    amounts = [
        int(usdt.balanceOf(vault) * DUSTY),
        int(usdc.balanceOf(vault) * DUSTY),
        int(dai.balanceOf(vault) * DUSTY)
    ]

    vault.balancer.deposit_and_stake(underlyings, amounts)

    for token, amount in min_amounts.items():
            balance_checker.verifyBalance(
                token,
                vault,
                amount
            )

    vault.print_snapshot()
    vault.post_safe_tx(skip_preview=True)
