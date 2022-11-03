from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    dev_msig = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)

    dev_msig.init_rari()

    # only set pause guardian
    dev_msig.rari.set_pause_guardian(registry.eth.guardian)

    dev_msig.post_safe_tx()
