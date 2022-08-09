from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from rich.console import Console
from helpers.constants import AddressZero

C = Console()

TECH_OPS = registry.eth.badger_wallets.techops_multisig
DEV = registry.eth.badger_wallets.dev_multisig

REGISTRY = registry.eth.registry_v2

BBB_A_USD = registry.eth.sett_vaults.bBB_a_USD

# Changes bb-a-usd's metadata to reflect new type: None
def change_vault_type():
    safe = GreatApeSafe(TECH_OPS)
    safe.init_badger()

    registry = safe.contract(REGISTRY)

    # Currently name=bb-a-USD,protocol=Aura,behavior=Ecosystem
    safe.badger.update_metadata(BBB_A_USD, "name=bb-a-USD,protocol=Aura,behavior=None")
    info = registry.productionVaultInfoByVault(BBB_A_USD)
    assert info[3] == "name=bb-a-USD,protocol=Aura,behavior=None"

    safe.post_safe_tx()


# Sets the withdrawal fee on bb-a-usd to 0.1% since it is not a helper anymore
def change_vault_withdrawal_fee():
    safe = GreatApeSafe(DEV)

    vault = interface.ITheVault(BBB_A_USD, owner=safe.account)

    vault.setWithdrawalFee(10)
    assert vault.withdrawalFee() == 10

    safe.post_safe_tx()


