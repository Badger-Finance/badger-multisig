from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface


DUSTY = 0.99

trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
vault.init_curve()
vault.init_convex()
vault.init_aave()
vault.init_compound()
vault.init_balancer()
vault.init_uni_v3()

balance_checker = interface.IBalanceChecker(
    registry.eth.helpers.balance_checker, owner=vault.account
)

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
bpt3pool_gauge_addr = vault.balancer.gauge_factory.getPoolGauge(bpt3pool)

crv = vault.contract(registry.eth.treasury_tokens.CRV)
cvx = vault.contract(registry.eth.treasury_tokens.CVX)
angle = vault.contract(registry.eth.bribe_tokens_claimable.ANGLE)
wbtc = vault.contract(registry.eth.treasury_tokens.WBTC)
badger = vault.contract(registry.eth.treasury_tokens.BADGER)

tokens = [
    usdt.address,
    usdc.address,
    dai.address,
    fei.address,
    eurs.address,
    crv3pool.address,
    crv3eur.address,
    crvfrax.address,
    ausdc.address,
    ausdt.address,
    cdai.address,
    afei.address,
    bpt3pool.address,
    bpt3pool_gauge_addr,
    crv.address,
    cvx.address,
    angle.address,
    wbtc.address,
    badger.address,
]


def main():
    vault.take_snapshot(tokens)

    min_amounts = {
        ausdc: 600_000e6,
        ausdt: 600_000e6,
        cdai: 27_000_000e8,
        afei: 300_000e18,
    }

    # withdrawals
    vault.convex.unstake_all_and_withdraw_all(crv3pool)
    vault.convex.unstake_all_and_withdraw_all(crv3eur)
    vault.convex.unstake_all_and_withdraw_all(crvfrax)
    vault.curve.withdraw_to_one_coin(crv3eur, crv3eur.balanceOf(vault), eurs)
    vault.curve.withdraw_to_one_coin(crvfrax, crvfrax.balanceOf(vault), crv3pool)

    # acquire enough of each stable for depositing
    # 600k dai + 300k for fei + 100k for balancer
    vault.curve.withdraw_to_one_coin(
        crv3pool, (615_000e18 + 310_000e18 + 105_000e18), dai
    )
    # 300k fei
    vault.curve.swap(dai, fei, 310_000e18)
    # swap eurs for usdc; not enough to make aave deposit
    vault.curve.swap(eurs, usdc, eurs.balanceOf(vault) * DUSTY)
    # so bit of extra usdc + 100k for balancer
    vault.curve.withdraw_to_one_coin(crv3pool, 30_000e18 + 105_000e18, usdc)
    # 600k usdt + 100k for balancer
    vault.curve.withdraw_to_one_coin(crv3pool, 615_000e18 + 105_000e18, usdt)

    # deposits
    vault.aave.deposit(usdc, 614_746e6)
    vault.aave.deposit(usdt, 614_746e6)
    vault.aave.deposit(fei, 307_373e18)
    vault.compound.deposit(dai, 614_746e18)

    for token, amount in min_amounts.items():
        balance_checker.verifyBalance(token, vault, amount)

    # bonus: collect univ3 fees
    vault.uni_v3.collect_fees()

    vault.print_snapshot()
    vault.post_safe_tx(skip_preview=True)


def deposit_bal3pool():
    vault.take_snapshot(tokens)

    # balancer deposit
    underlyings = [usdt, usdc, dai]
    amounts = [int(102_457e6), int(102_457e6), int(102_457e18)]
    vault.balancer.deposit_and_stake(underlyings, amounts)
    balance_checker.verifyBalance(bpt3pool_gauge_addr, vault, 300_000e18)

    vault.print_snapshot()
    vault.post_safe_tx()


def sweep_to_trops():
    trops.take_snapshot(tokens)
    vault.take_snapshot(tokens)

    # stake last 1% of bal3pool
    vault.balancer.stake_all(bpt3pool)

    for addr in [
        ausdc.address,
        ausdt.address,
        afei.address,
        cdai.address,
        bpt3pool.address,
        bpt3pool_gauge_addr,
        badger.address,
    ]:
        tokens.remove(addr)

    for addr in tokens:
        token = interface.ERC20(addr, owner=vault.account)
        token.transfer(trops, token.balanceOf(vault))

    trops.print_snapshot()
    vault.print_snapshot()

    vault.post_safe_tx()
