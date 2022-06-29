from brownie import DummyController, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    stabiliser = safe.contract(
        r.strategies['experimental.digg'], interface.IStabilizeStrategyDiggV1
    )
    digg = safe.contract(r.treasury_tokens.DIGG)
    wbtc = safe.contract(r.treasury_tokens.WBTC)
    renbtc = safe.contract(r.treasury_tokens.renBTC)
    yvwbtc = safe.contract(r.treasury_tokens.yvWBTC)
    imbtc = safe.contract(r.mstable_vaults.imBTC)
    fpmbtchbtc = safe.contract(r.mstable_vaults.FpMbtcHbtc)
    dummy = DummyController.at(r.controllers.dummy)

    tokens = [digg, wbtc, renbtc, yvwbtc, imbtc, fpmbtchbtc]
    safe.take_snapshot(tokens)
    trops.take_snapshot(tokens)

    stabiliser.governancePullSomeCollateral(wbtc.balanceOf(stabiliser))
    stabiliser.setController(dummy)
    dummy.sweepStratToTrops(stabiliser, {'from': safe.account})

    # do a sweep of all assets from dev to trops
    digg.transfer(trops, digg.balanceOf(safe))
    wbtc.transfer(trops, wbtc.balanceOf(safe))
    renbtc.transfer(trops, renbtc.balanceOf(safe))
    imbtc.transfer(trops, imbtc.balanceOf(safe))
    fpmbtchbtc.transfer(trops, fpmbtchbtc.balanceOf(safe))
    yvwbtc.withdraw(yvwbtc.balanceOf(safe), trops)
    safe.account.transfer(trops, safe.account.balance())

    trops.print_snapshot()
    safe.post_safe_tx()
