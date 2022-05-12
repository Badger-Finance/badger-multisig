from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from decimal import Decimal

def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    safe.init_balancer()

    badger = safe.contract(registry.eth.treasury_tokens.BADGER)
    wbtc = safe.contract(registry.eth.treasury_tokens.WBTC)
    bpt = safe.contract(registry.eth.balancer.B_20_BTC_80_BADGER)
    staked_bpt = safe.contract(safe.balancer.gauge_factory.getPoolGauge(bpt))

    safe.take_snapshot([badger, wbtc, bpt.address, staked_bpt.address])

    underlyings = [wbtc, badger]
    safe.balancer.unstake_all_and_withdraw_all(underlyings)

    safe.print_snapshot()
    safe.post_safe_tx()