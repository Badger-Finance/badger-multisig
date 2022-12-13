from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():

    bpts = [
        r.balancer.B_20_BTC_80_BADGER,
        r.balancer.B_50_BADGER_50_RETH,
        r.balancer.bpt_40wbtc_40digg_20graviaura,
    ]

    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_balancer()
    vault.take_snapshot(bpts)

    for bpt in bpts:
        vault.balancer.stake_all(vault.contract(bpt))

    vault.post_safe_tx()
