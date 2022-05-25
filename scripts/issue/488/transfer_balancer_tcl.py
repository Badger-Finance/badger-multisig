from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    trops.init_balancer()

    bpt_20BTC_80_BADGER = trops.contract(registry.eth.balancer.B_20_BTC_80_BADGER)
    bpt_20BTC_80_BADGER_GAUGE = trops.contract(
        registry.eth.balancer.B_20_BTC_80_BADGER_GAUGE
    )

    trops.take_snapshot(
        tokens=[bpt_20BTC_80_BADGER.address, bpt_20BTC_80_BADGER_GAUGE.address]
    )
    vault.take_snapshot(tokens=[bpt_20BTC_80_BADGER_GAUGE.address])

    trops.balancer.stake_all(bpt_20BTC_80_BADGER)

    bal = bpt_20BTC_80_BADGER_GAUGE.balanceOf(trops)

    bpt_20BTC_80_BADGER_GAUGE.transfer(vault, bal)

    vault.print_snapshot()

    trops.post_safe_tx()
