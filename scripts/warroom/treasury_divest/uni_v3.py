from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_uni_v3()

    badger = vault.contract(r.treasury_tokens.BADGER)
    wbtc = vault.contract(r.treasury_tokens.WBTC)
    gtc = vault.contract(r.treasury_tokens.GTC)

    vault.take_snapshot(tokens=[badger, wbtc, gtc])

    vault_ids = [
        vault.uni_v3.nonfungible_position_manager.tokenOfOwnerByIndex(vault, x)
        for x in range(vault.uni_v3.nonfungible_position_manager.balanceOf(vault))
    ]

    for vault_id in vault_ids:
        vault.uni_v3.burn_token_id(vault_id)

    vault.post_safe_tx()
