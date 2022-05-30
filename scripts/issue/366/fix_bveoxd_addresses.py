from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.ftm.badger_wallets.dev_multisig)

    bveoxd = safe.contract(registry.ftm.sett_vaults.bveOXD)

    bveoxd.setTreasury(registry.ftm.badger_wallets.treasury_ops_multisig)
    bveoxd.setStrategist(registry.ftm.badger_wallets.techops_multisig)

    safe.post_safe_tx()