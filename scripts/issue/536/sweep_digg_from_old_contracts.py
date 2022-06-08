from brownie import DummyController, accounts, interface

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
    dummy = DummyController.deploy({'from': accounts[0]})

    safe.take_snapshot([digg, wbtc])
    trops.take_snapshot([digg, wbtc])

    stabiliser.governancePullSomeCollateral(wbtc.balanceOf(stabiliser))
    stabiliser.setController(dummy)
    dummy.sweepStratToTrops(stabiliser, {'from': safe.account})

    trops.print_snapshot()
    safe.post_safe_tx()
