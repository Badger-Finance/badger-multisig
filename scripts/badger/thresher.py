from brownie import Contract, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


DUSTY = .995
SLIPPAGE = .99

SAFE = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
VAULT = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
VOTER = GreatApeSafe(registry.eth.badger_wallets.treasury_voter_multisig)

ZAP = SAFE.contract(registry.eth.curve.zap_ibbtc)
BIBBTC = SAFE.contract(registry.eth.sett_vaults.bcrvIbBTC)
BSLPIBBTC = SAFE.contract(registry.eth.sett_vaults.bslpWbtcibBTC)
IBBTC_LP = SAFE.contract(registry.eth.treasury_tokens.crvIbBTC)
IBBTC = SAFE.contract(registry.eth.treasury_tokens.ibBTC)
WIBBTC = SAFE.contract(registry.eth.treasury_tokens.wibBTC)
SBTC_LP = SAFE.contract(registry.eth.treasury_tokens.crvSBTC)
YVWBTC = SAFE.contract(registry.eth.treasury_tokens.yvWBTC)
BYVWBTC = SAFE.contract(registry.eth.yearn_vaults.byvWBTC)
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
AURABAL = SAFE.contract(registry.eth.treasury_tokens.AURABAL)
WETH = SAFE.contract(registry.eth.treasury_tokens.WETH)
DIGG = SAFE.contract(registry.eth.treasury_tokens.DIGG)
BADGER = SAFE.contract(registry.eth.treasury_tokens.BADGER)
BAL = SAFE.contract(registry.eth.treasury_tokens.BAL)


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
    setts.pop('bBADGER')  # dust currently
    setts.pop('graviAURA')
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
                SAFE.curve.withdraw_to_one_coin(lp, bal_start, WBTC)
            except:
                try:
                    SAFE.curve.withdraw_to_one_coin(lp, bal_start, SBTC_LP)
                except:
                    try:
                        SAFE.curve.withdraw_to_one_coin(lp, bal_start, THREEPOOL)
                    except:
                        SAFE.curve.withdraw(lp, bal_start)

    # exception: yearn vault and its sett
    if BYVWBTC.balanceOf(SAFE):
        BYVWBTC.withdraw()
    if YVWBTC.balanceOf(SAFE):
        YVWBTC.withdraw()


def consolidate_to_wbtc():
    # unwrap wibbtc
    WIBBTC.burn(WIBBTC.balanceToShares(WIBBTC.balanceOf(SAFE)))

    # zap ibbtc, renbtc and sbtc into the ibbtc_lp
    dep_ibbtc = IBBTC.balanceOf(SAFE) * DUSTY
    dep_renbtc = RENBTC.balanceOf(SAFE) * DUSTY
    dep_wbtc = 0
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

    # withdraw the ibbtc_lp to sbtc_lp and withdraw the sbtc_lp to wbtc
    SAFE.curve.withdraw_to_one_coin(
        IBBTC_LP, IBBTC_LP.balanceOf(SAFE) * DUSTY, SBTC_LP
    )
    SAFE.curve.withdraw_to_one_coin(
        SBTC_LP, SBTC_LP.balanceOf(SAFE) * DUSTY, WBTC
    )


def main():
    """
    drive around the farm with the thresher and turn all yield and fees into
    an asset worthy of the treasury vault:
    - badger, digg
    - wbtc
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
    SAFE.init_balancer()

    # 1: deposit usdc, usdt and dai into 3pool
    consolidate_stables()

    # 2: make cvx, cvxcrv and crv productive by dogfooding
    dogfood_curve_convex()

    # 3: unwind every possible lp (uni, sushi, crv)
    BIBBTC.withdrawAll()
    BSLPIBBTC.withdrawAll()
    unwind_lps()

    # 4: consolidate btc positions to $wbtc
    consolidate_to_wbtc()

    # 5: unwind xsushi
    SAFE.sushi.xsushi.leave(SAFE.sushi.xsushi.balanceOf(SAFE))

    # 6: send all relevant influence tokens to voter
    SAFE.balancer.claim([BADGER, WBTC])
    BAL.transfer(VOTER, BAL.balanceOf(SAFE))
    AURABAL.transfer(VOTER, AURABAL.balanceOf(SAFE))
    BVECVX.transfer(VOTER, BVECVX.balanceOf(SAFE))

    # 7: send weth to vault
    WETH.transfer(VAULT, WETH.balanceOf(SAFE) * DUSTY)

    # 8: send all digg to vault
    DIGG.transfer(VAULT, DIGG.balanceOf(SAFE))

    SAFE.post_safe_tx()

    # TODO
    # fPmBTCHBTC and imBTC to wbtc
