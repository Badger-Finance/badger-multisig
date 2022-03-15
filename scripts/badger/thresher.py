from brownie import Contract, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


DUSTY = .995
SLIPPAGE = .99

SAFE = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
VAULT = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)

ZAP = SAFE.contract(registry.eth.curve.zap_ibbtc)
BIBBTC = interface.ISettV4h(
    registry.eth.sett_vaults.bcrvIbBTC, owner=SAFE.account
)
IBBTC_LP = SAFE.contract(registry.eth.treasury_tokens.crvIbBTC)
IBBTC = interface.ERC20(registry.eth.treasury_tokens.ibBTC, owner=SAFE.account)
SBTC_LP = SAFE.contract(registry.eth.treasury_tokens.crvSBTC)
RENBTC = interface.ERC20(
    registry.eth.treasury_tokens.renBTC, owner=SAFE.account
)
WBTC = interface.ERC20(registry.eth.treasury_tokens.WBTC, owner=SAFE.account)
SBTC = interface.ERC20(registry.eth.treasury_tokens.sBTC, owner=SAFE.account)
CRV = interface.ERC20(registry.eth.treasury_tokens.CRV, owner=SAFE.account)
CVX = interface.ERC20(registry.eth.treasury_tokens.CVX, owner=SAFE.account)
CVXCRV = interface.ERC20(registry.eth.treasury_tokens.cvxCRV, owner=SAFE.account)
BCVX = interface.ISettV4h(
    registry.eth.treasury_tokens.bCVX, owner=SAFE.account
)
BCVXCRV = interface.ISettV4h(
    registry.eth.sett_vaults.bcvxCRV, owner=SAFE.account
)
BVECVX = interface.ISettV4h(
    registry.eth.sett_vaults.bveCVX, owner=SAFE.account
)
THREEPOOL = SAFE.contract(registry.eth.treasury_tokens.crv3pool)
DAI = interface.ERC20(registry.eth.treasury_tokens.DAI, owner=SAFE.account)
USDC = interface.ERC20(registry.eth.treasury_tokens.USDC, owner=SAFE.account)
USDT = interface.ERC20(registry.eth.treasury_tokens.USDT, owner=SAFE.account)


def consolidate_stables():
    amounts = [DAI.balanceOf(SAFE), USDC.balanceOf(SAFE), USDT.balanceOf(SAFE)]
    if sum(amounts) > 0:
        SAFE.curve.deposit(THREEPOOL, amounts)


def dogfood_curve_convex():
    if CRV.balanceOf(SAFE) > 0:
        SAFE.curve.swap(CRV, CVXCRV, CRV.balanceOf(SAFE))
    if CVXCRV.balanceOf(SAFE) > 0:
        CVXCRV.approve(BCVXCRV, 2**256-1)
        BCVXCRV.depositAll()
        CVXCRV.approve(BCVXCRV, 0)
    if BCVX.balanceOf(SAFE) > 0:
        BCVX.withdraw(BCVX.balanceOf(SAFE))
    if CVX.balanceOf(SAFE) > 0:
        CVX.approve(BVECVX, 2**256-1)
        BVECVX.depositAll()
        CVX.approve(BVECVX, 0)


def unwind_lps():
    # build list with lp token labels
    lps = []
    for lp in registry.eth.treasury_tokens.keys():
        if lp.startswith('uni') or lp.startswith('slp') or lp.startswith('crv'):
            lps.append(lp)

    # withdraw from uni and sushi lps
    for label in lps:
        lp = Contract(registry.eth.treasury_tokens[label], owner=SAFE.account)
        bal_start = lp.balanceOf(SAFE)
        if bal_start <= 0:
            continue
        if label.startswith('uni'):
            SAFE.uni_v2.remove_liquidity(lp, bal_start)
        if label.startswith('slp'):
            SAFE.sushi.remove_liquidity(lp, bal_start)

    # since some btokens hold curve lps we withdrawall btokens, except for
    # productive ones
    setts = registry.eth.sett_vaults.copy()
    setts.pop('bcrvIbBTC')
    setts.pop('bcvxCRV')
    setts.pop('bveCVX')
    setts.pop('bbveCVX-CVX-f')
    setts.pop('remDIGG')
    for addr in setts.values():
        sett = interface.ISettV4h(addr, owner=SAFE.account)
        if sett.balanceOf(SAFE) > 0:
            sett.withdrawAll()

    # withdraw from curve lps
    for label in lps:
        if label == 'crv3pool':
            continue
        lp = Contract(registry.eth.treasury_tokens[label], owner=SAFE.account)
        bal_start = lp.balanceOf(SAFE)
        if bal_start <= 0:
            continue
        if label.startswith('crv'):
            try:
                SAFE.curve.withdraw_to_one_coin(lp, bal_start, SBTC_LP)
            except:
                try:
                    SAFE.curve.withdraw_to_one_coin(lp, bal_start, WBTC)
                except:
                    try:
                        SAFE.curve.withdraw_to_one_coin(lp, bal_start, THREEPOOL)
                    except:
                        SAFE.curve.withdraw(lp, bal_start)


def dogfood_btc():
    # zap ibbtc, renbtc, wbtc and sbtc into the ibbtc_lp
    dep_ibbtc = IBBTC.balanceOf(SAFE) * DUSTY
    dep_renbtc = RENBTC.balanceOf(SAFE) * DUSTY
    dep_wbtc = WBTC.balanceOf(SAFE) * DUSTY
    dep_sbtc = SBTC.balanceOf(SAFE) * DUSTY
    expected = ZAP.calc_token_amount(
        IBBTC_LP,
        [dep_ibbtc, dep_renbtc, dep_wbtc, dep_sbtc],
        True
    )
    if dep_ibbtc > 0:
        IBBTC.approve(ZAP, dep_ibbtc)
    if dep_renbtc > 0:
        RENBTC.approve(ZAP, dep_renbtc)
    if dep_wbtc > 0:
        WBTC.approve(ZAP, dep_wbtc)
    if dep_sbtc > 0:
        SBTC.approve(ZAP, dep_sbtc)
    ZAP.add_liquidity(
        IBBTC_LP,
        [dep_ibbtc, dep_renbtc, dep_wbtc, dep_sbtc],
        expected * SLIPPAGE
    )

    # deposit sbtc_lp directly into ibbtc_lp
    if SBTC_LP.balanceOf(SAFE) > 0:
        SAFE.curve.deposit(IBBTC_LP, [0, SBTC_LP.balanceOf(SAFE) * DUSTY])

    # finally dogfood all into our own ibbtc sett
    if IBBTC_LP.balanceOf(SAFE) > 0:
        IBBTC_LP.approve(BIBBTC, 2**256-1)
        BIBBTC.depositAll()
        IBBTC_LP.approve(BIBBTC, 0)


def main():
    """
    drive around the farm with the thresher and turn all yield and fees into
    an asset worthy of the treasury vault:
    - badger, digg
    - bibbtc
    - weth
    - 3pool
    - bvecvx, bcvxcrv
    """

    SAFE.take_snapshot(
        list(registry.eth.treasury_tokens.values()) + \
        list(registry.eth.sett_vaults.values())
    )

    SAFE.init_uni_v2()
    SAFE.init_sushi()
    SAFE.init_curve()

    # 1: deposit usdc, usdt and dai into 3pool
    consolidate_stables()

    # 2: make cvx, cvxcrv and crv productive by dogfooding
    dogfood_curve_convex()

    # 3: unwind every possible lp (uni, sushi, crv)
    unwind_lps()

    # 4: dusty dogfooding of btc variants
    dogfood_btc()

    SAFE.post_safe_tx(skip_preview=True)
