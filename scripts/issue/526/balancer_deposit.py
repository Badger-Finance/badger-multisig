from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from decimal import Decimal


WBTC_AMOUNT = 15


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    safe.init_balancer()

    badger = safe.contract(registry.eth.treasury_tokens.BADGER)
    wbtc = safe.contract(registry.eth.treasury_tokens.WBTC)
    bpt = safe.contract(registry.eth.balancer.B_20_BTC_80_BADGER)
    staked_bpt = safe.contract(safe.balancer.gauge_factory.getPoolGauge(bpt))

    safe.take_snapshot([badger, wbtc, bpt.address, staked_bpt.address])

    wbtc_to_deposit = int(Decimal(WBTC_AMOUNT) * Decimal(10 ** wbtc.decimals()))
    ratio = bpt.getNormalizedWeights()[0] / bpt.getNormalizedWeights()[1]
    badger_to_deposit = int(
        safe.balancer.get_amount_out(wbtc, badger, 1000)
        / 1000
        * wbtc_to_deposit
        / 0.997
        / ratio
    )

    underlyings = [wbtc, badger]
    amounts = [wbtc_to_deposit, badger_to_deposit]
    safe.balancer.deposit_and_stake(underlyings, amounts)

    safe.print_snapshot()
    safe.post_safe_tx()
