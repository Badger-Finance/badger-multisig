from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    safe.init_maker()
    safe.maker.build_proxy()
    safe.post_safe_tx(call_trace=True)
