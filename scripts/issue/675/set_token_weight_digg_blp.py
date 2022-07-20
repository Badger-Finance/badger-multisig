from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)

    emission_control = techops.contract(r.EmissionControl)

    emission_control.setTokenWeight(r.sett_vaults.b40WBTC_40DIGG_20graviAURA, 4000)

    techops.post_safe_tx()
