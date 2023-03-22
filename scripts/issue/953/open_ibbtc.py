from brownie import Contract, Wei, interface
from helpers.constants import MaxUint256
from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

# Tokens
BCRVREN_STRAT = registry.eth.strategies["native.renCrv"]
BCRVIBBTC_STRAT = registry.eth.strategies["native.bcrvIbBTC"]
# Peaks
BADGER_PEAK = registry.eth.peaks.badgerPeak

C = Console()


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)

    # Change Peak's status
    # enum PeakState { Extinct, Active, RedeemOnly, MintOnly }
    core = interface.ICore(registry.eth.ibBTC.core, owner=safe.account)
    core.setPeakStatus(BADGER_PEAK, 2)

    # Remove fees
    bcrvRenBTC_strat = safe.contract(BCRVREN_STRAT)
    bcrvIbBTC_strat = safe.contract(BCRVIBBTC_STRAT)

    bcrvRenBTC_strat.setWithdrawalFee(0)
    bcrvIbBTC_strat.setWithdrawalFee(0)

    safe.post_safe_tx()
