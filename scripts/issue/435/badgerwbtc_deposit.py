from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from decimal import Decimal

def main(amount_wbtc_ether=3):
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    safe.init_balancer()

    badger = safe.contract(registry.eth.treasury_tokens.BADGER)
    wbtc = safe.contract(registry.eth.treasury_tokens.WBTC)
    bpt = safe.contract(registry.eth.balancer.B_20_BTC_80_BADGER)
    staked_bpt = safe.contract(safe.balancer.gauge_factory.getPoolGauge(bpt))

    safe.take_snapshot([badger, wbtc, bpt.address, staked_bpt.address])

    wbtc_to_deposit = int(Decimal(amount_wbtc_ether) * Decimal(10 ** wbtc.decimals()))
    wbtc_badger_rate = safe.balancer.get_amount_out(badger, wbtc, 1e18)
    badger_to_deposit = int( (wbtc_to_deposit / wbtc_badger_rate * 1e18) * 4 )

    underlyings = [wbtc, badger]
    amounts = [wbtc_to_deposit, badger_to_deposit]
    safe.balancer.deposit_and_stake(underlyings, amounts)

    safe.print_snapshot()
    safe.post_safe_tx()
