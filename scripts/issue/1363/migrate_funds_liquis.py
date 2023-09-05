from helpers.addresses import r
from great_ape_safe import GreatApeSafe


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_bunni(r.bunni.badger_wbtc_bunni_token_309720_332580)
    vault.init_liquis()

    bunni_lp = vault.contract(r.bunni.badger_wbtc_bunni_token_309720_332580)

    vault.bunni.unstake(r.bunni.badger_wbtc_bunni_gauge_309720_332580)

    vault.liquis.deposit_all_and_stake(bunni_lp)

    vault.post_safe_tx()
