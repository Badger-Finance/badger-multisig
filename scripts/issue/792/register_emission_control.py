from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import chain


chain_safe = GreatApeSafe(r.badger_wallets.techops_multisig)
chain_safe.init_badger()


def main():
    if chain.id not in [1, 42161]:
        raise Exception("Invalid chain")
    chain_safe.badger.set_key_on_registry("emissionControl", r.EmissionControl)
    chain_safe.post_safe_tx()
