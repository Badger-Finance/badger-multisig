from brownie import Contract, Wei, interface
from helpers.constants import MaxUint256
from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

# Tokens
POOL = registry.eth.crv_pools.crvIbBTC
WBTC = registry.eth.treasury_tokens.WBTC
IBBTC = registry.eth.treasury_tokens.ibBTC
WIBBTC = registry.eth.treasury_tokens.wibBTC
BYVWBTC = registry.eth.yearn_vaults.byvWBTC

# Peaks
BADGER_PEAK = registry.eth.peaks.badgerPeak
YEARN_PEAK = registry.eth.peaks.byvWbtcPeak

# Zaps
WBTC_ZAP = registry.ibbtc.mint_zap

WBTC_IN = 30e8  # to use to rebalance
MIN_WBTC_OUT = 29.98e8

C = Console()

def main(simulation="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_curve()
    safe.init_curve_v2()

    # Tokens
    wbtc = safe.contract(WBTC)
    ibbtc = safe.contract(IBBTC)
    # Peaks
    badger_peak = safe.contract(BADGER_PEAK)
    yearn_peak = Contract.from_explorer(YEARN_PEAK, owner=safe.account)
    # Vaults
    byvwbtc = interface.ISimpleWrapperGatedUpgradeable(BYVWBTC, owner=safe.account)
    # Zaps
    zap = interface.IZap(WBTC_ZAP, owner=safe.account)

    if simulation == "true":
        set_ibbtc_peaks_status(simulation)
        vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
        vault_balance = wbtc.balanceOf(vault.account)
        wbtc.transfer(safe.account, wbtc.balanceOf(vault.account), {"from": vault.account})
        assert wbtc.balanceOf(safe.account) >= vault_balance

    # 1. Approvals
    wbtc.approve(BYVWBTC, MaxUint256)
    byvwbtc.approve(YEARN_PEAK, MaxUint256)
    ibbtc.approve(WBTC_ZAP, MaxUint256)

    # Loop: Do the following multiple things until fullly rebalanced

    # 2. Deposit in byvWBTC
    byvwbtc_balance_before = byvwbtc.balanceOf(safe.account)
    tx = byvwbtc.deposit(WBTC_IN, ["0x0"])
    shares = tx.events["Transfer"][1]["value"]
    byvwbtc_balance_after = byvwbtc.balanceOf(safe.account)
    assert shares == byvwbtc_balance_after - byvwbtc_balance_before

    # 3. Mint ibBTC with byvWBTC
    ibbtc_before = ibbtc.balanceOf(safe.account)
    yearn_peak.mint(shares, ["0x0"])
    ibbtc_after = ibbtc.balanceOf(safe.account)
    ibbtc_gained = ibbtc_after - ibbtc_before

    # 4. Redeem from renCrv
    min_out = zap.calcRedeemInWbtc(ibbtc_gained)
    wbtc_out = zap.redeem(WBTC, ibbtc_gained, 0, 1, min_out)

    # End of cycle

    # 1. Approvals
    wbtc.approve(BYVWBTC, 0)
    byvwbtc.approve(YEARN_PEAK, 0)
    ibbtc.approve(WBTC_ZAP, 0)


    C.print("WBTC OUT", wbtc_out)

    # safe.post_safe_tx()


# Turning minting on for YearnPeak and minting off for BadgerPeak
# enum PeakState { Extinct, Active, RedeemOnly, MintOnly }
def set_ibbtc_peaks_status(simulation="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)

    core = interface.ICore(registry.eth.ibBTC.core, owner=safe.account)

    core.setPeakStatus(BADGER_PEAK, 2)
    core.setPeakStatus(YEARN_PEAK, 1)

    if simulation == "false":
        safe.post_safe_tx()