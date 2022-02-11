from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    """
    adjust rate models on our fuse-22 rari pool.
    rate models via https://docs.fei.money/developer/contract-addresses
    https://github.com/Badger-Finance/badger-multisig/issues/101
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_rari()

    for label, addr in registry.eth.rari.items():
        if label.endswith('-22'):
            if label.startswith('fETH') or label.startswith('fWBTC'):
                safe.rari.ftoken_set_rate_model(
                    addr, registry.eth.fei.jump_rate_model_fei_eth
                )
            else:
                safe.rari.ftoken_set_rate_model(
                    addr, registry.eth.fei.jump_rate_model_fei_dai
                )
    safe.post_safe_tx()
