from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def enable_module():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)

    safe = interface.IGnosisSafe_v1_3_0(
        r.badger_wallets.treasury_vault_multisig, owner=vault.account
    )

    safe.enableModule(r.safe_modules.treasury_vault.univ3_harvester)

    vault.post_safe_tx()


def add_member():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)
    upkeep_manager = techops.contract(r.badger_wallets.upkeep_manager)

    upkeep_manager.addMember(
        r.safe_modules.treasury_vault.univ3_harvester,
        "UniswapV3Harvester",
        # gas figure ref: https://github.com/Badger-Finance/badger-multisig/issues/1154#issuecomment-1453651104
        568_000,
        0,
    )

    techops.post_safe_tx()
