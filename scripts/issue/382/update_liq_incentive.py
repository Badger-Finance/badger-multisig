from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main(new_incentive):
    # ex 10% incentive: new_incentive = '1.10'

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_rari()

    safe.rari.set_liquidation_incentive(float(new_incentive))

    safe.post_safe_tx(events=True)
