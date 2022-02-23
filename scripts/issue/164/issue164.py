from scripts.badger.whitelist import all_setts
from helpers.addresses import registry

def main():
    """
    whitelist treasury_vault_multisig to all setts
    """

    msig_to_whitelist = registry.eth.badger_wallets.treasury_vault_multisig
    all_setts(msig_to_whitelist)