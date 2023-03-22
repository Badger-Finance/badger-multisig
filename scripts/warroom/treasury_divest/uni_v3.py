from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_uni_v3()

    vault_ids = [
        vault.uni_v3.nonfungible_position_manager.tokenOfOwnerByIndex(vault, x)
        for x in range(vault.uni_v3.nonfungible_position_manager.balanceOf(vault))
    ]

    tokens = [
        vault.uni_v3.nonfungible_position_manager.positions(vault_id)[2:4]
        for vault_id in vault_ids
    ]
    tokens = list(set([token for pair in tokens for token in pair]))

    vault.take_snapshot(tokens=tokens)

    for vault_id in vault_ids:
        vault.uni_v3.burn_token_id(vault_id)

    vault.post_safe_tx()
