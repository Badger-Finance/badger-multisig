from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


LIQUIDATION_INCENTIVE = 1.12


def main():

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_rari()

    safe.rari.set_liquidation_incentive(LIQUIDATION_INCENTIVE)

    safe.post_safe_tx(events=True)
