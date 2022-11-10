from brownie import Contract, Wei, interface
from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

POOL = registry.eth.crv_pools.crvIbBTC
WBTC = registry.eth.treasury_tokens.WBTC
IBBTC = registry.eth.treasury_tokens.ibBTC
WIBBTC = registry.eth.treasury_tokens.wibBTC
BYVWBTC = registry.eth.yearn_vaults.byvwbtc
BADGER_PEAK = registry.eth.peaks.badgerPeak
YEARN_PEAK = registry.eth.peaks.badgerPeak

WBTC_AMOUNT = 1e8  # to use to rebalance

C = Console()



def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    safe.init_curve()
    safe.init_curve_v2()


    safe.post_safe_tx()


# Turning minting on for YearnPeak and minting off for BadgerPeak
# enum PeakState { Extinct, Active, RedeemOnly, MintOnly }
def set_ibbtc_peaks_status():
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)

    core = interface.ICore(registry.eth.ibBTC.core, owner=safe.account)

    core.setPeakStatus(BADGER_PEAK, 2)
    core.setPeakStatus(YEARN_PEAK, 1)

    safe.post_safe_tx()

