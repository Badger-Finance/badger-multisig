from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def set_affiliate():
    dev_msig = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    byvWBTC = dev_msig.contract(registry.eth.yearn_vaults.byvWBTC)

    byvWBTC.setAffiliate(registry.eth.badger_wallets.treasury_ops_multisig)

    dev_msig.post_safe_tx()


def accept_affiliate():
    vault_msig = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    byvWBTC = vault_msig.contract(registry.eth.yearn_vaults.byvWBTC)

    byvWBTC.acceptAffiliate()

    vault_msig.post_safe_tx()
