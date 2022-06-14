from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
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
    slp = safe.contract(r.sett_vaults.bslpWbtcibBTC)
    bpt_badgerwbtc = safe.contract(r.balancer.B_20_BTC_80_BADGER)
    bvecvx = safe.contract(r.treasury_tokens.bveCVX)

    safe.take_snapshot([
        badger, usdc, weth, bal, usdt, dai, eurs, crv, cvx, fei, angle,
        threepool, slp, bpt_badgerwbtc, bvecvx
    ])

    # badger for emissions, rembadger, bribes and contribs
    badger.transfer(r.drippers.tree_2022_q2, 260_000e18)
    badger.transfer(r.drippers.rembadger_2022_q2, 75_000e18)
    badger.transfer(r.badger_wallets.treasury_ops_multisig, 104_000e18)
    badger.transfer(r.badger_wallets.payments_multisig, 90_000e18) # guestimate, wait for mason

    # usdc for contribs
    usdc.transfer(r.badger_wallets.payments_multisig, 900_000e6)

    # bal to voter for locking to aurabal
    bal.transfer(r.badger_wallets.bvecvx_voting_multisig, bal.balanceOf(safe))

    # stake ~$7k worth of bpt
    safe.init_balancer()
    safe.balancer.stake_all(bpt_badgerwbtc)

    # dust to trops for processing
    for dust in [wbtc, usdc, usdt, dai, eurs, crv, cvx, fei, angle, threepool, slp]:
        dust.transfer(
            r.badger_wallets.treasury_ops_multisig, dust.balanceOf(safe)
        )

    # consolidate eth into weth position
    weth.deposit({'value': safe.account.balance()})

    # bvecvx to treasury voter
    bvecvx.transfer(
        r.badger_wallets.bvecvx_voting_multisig, bvecvx.balanceOf(safe)
    )

    safe.post_safe_tx()
