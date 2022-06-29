from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    badger = safe.contract(r.treasury_tokens.BADGER)
    usdc = safe.contract(r.treasury_tokens.USDC)
    weth = safe.contract(r.treasury_tokens.WETH)
    wbtc = safe.contract(r.treasury_tokens.WBTC)
    bal = safe.contract(r.treasury_tokens.BAL)
    usdt = safe.contract(r.treasury_tokens.USDT)
    dai = safe.contract(r.treasury_tokens.DAI)
    eurs = safe.contract(r.treasury_tokens.EURS)
    crv = safe.contract(r.treasury_tokens.CRV)
    cvx = safe.contract(r.treasury_tokens.CVX)
    fei = safe.contract(r.treasury_tokens.FEI)
    angle = safe.contract(r.treasury_tokens.ANGLE)
    threepool = safe.contract(r.treasury_tokens.crv3pool)
    ibbtc_lp = safe.contract(r.treasury_tokens.crvIbBTC)
    slp = safe.contract(r.sett_vaults.bslpWbtcibBTC)
    bpt_badgerwbtc = safe.contract(r.balancer.B_20_BTC_80_BADGER)
    bpt_3pool = safe.contract(r.balancer.B_3POOL)
    bvecvx = safe.contract(r.treasury_tokens.bveCVX)

    safe.take_snapshot([
        badger, usdc, weth, wbtc, bal, usdt, dai, eurs, crv, cvx, fei, angle,
        threepool, ibbtc_lp, slp, bpt_badgerwbtc, bpt_3pool, bvecvx
    ])
    trops.take_snapshot([
        badger, usdc, weth, wbtc, bal, usdt, dai, eurs, crv, cvx, fei, angle,
        threepool, ibbtc_lp, slp, bpt_badgerwbtc, bpt_3pool, bvecvx
    ])

    # badger for emissions, rembadger, bribes and contribs q3
    badger.transfer(r.drippers.tree_2022_q3, 260_000e18)
    badger.transfer(r.drippers.rembadger_2022_q3, 75_000e18)
    badger.transfer(trops, 104_000e18)
    badger.transfer(r.badger_wallets.payments_multisig, 500_000e18 - 110_000e18)  # prob ~110k left at end of q2

    # usdc for contribs q3
    usdc.transfer(r.badger_wallets.payments_multisig, 1_200_000e6 - 250_000e6)  # ~250k left after payroll q2

    # claim bal and send to voter for locking to aurabal
    safe.init_balancer()
    safe.balancer.claim([wbtc, badger])
    bal.transfer(r.badger_wallets.treasury_voter_multisig, bal.balanceOf(safe))

    # stake ~$7k worth of dust bpt
    safe.init_balancer()
    safe.balancer.stake_all(bpt_badgerwbtc)

    # balancer 3pool deposit & stake;
    # https://github.com/Badger-Finance/badger-multisig/issues/413
    underlyings = [usdt, usdc, dai]
    amounts = [int(102_457e6), int(102_457e6), int(102_457e18)]
    safe.balancer.deposit_and_stake(underlyings, amounts)
    safe.balancer.stake_all(bpt_3pool, dusty=.995)

    # dust to trops for processing
    for dust in [
        wbtc, usdc, usdt, dai, eurs, crv, cvx, fei,
        angle, threepool, ibbtc_lp, slp
    ]:
        dust.transfer(trops, dust.balanceOf(safe))

    # consolidate eth into weth position
    weth.deposit({'value': safe.account.balance()})

    # bvecvx to treasury voter
    bvecvx.transfer(
        r.badger_wallets.treasury_voter_multisig, bvecvx.balanceOf(safe)
    )

    print(
        'bpt_badgerwbtc in gauge:',
        safe.contract(safe.balancer.gauge_factory.getPoolGauge(bpt_badgerwbtc)).balanceOf(safe)
    )
    print(
        'bpt_3pool in gauge:',
        safe.contract(safe.balancer.gauge_factory.getPoolGauge(bpt_3pool)).balanceOf(safe)
    )

    trops.print_snapshot()
    safe.post_safe_tx(skip_preview=True)
