from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    techops = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)

    emission_control = techops.contract(registry.eth.EmissionControl)

    emission_control.setTokenWeight(registry.eth.sett_vaults["b80BADGER-20WBTC"], 8000)

    techops.post_safe_tx()
