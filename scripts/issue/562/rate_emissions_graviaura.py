from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    techops = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)

    emission_control = techops.contract(registry.eth.EmissionControl)

    emission_control.setBoostedEmission(registry.eth.sett_vaults.graviAURA, 5000)

    techops.post_safe_tx()
