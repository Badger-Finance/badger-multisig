from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    usdc = vault.contract(r.treasury_tokens.USDC)
    vault.take_snapshot([usdc])
    usdc.transfer(r.gitcoin.matching_pools_funds, 250_000e6)
    vault.post_safe_tx()
