from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from decimal import Decimal

def main():
    dev_msig = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)

    dev_msig.init_rari()

    bveCVX = dev_msig.contract(registry.eth.sett_vaults.bveCVX)

    single_side_liq = bveCVX.balanceOf(registry.eth.crv_meta_pools["bveCVX-CVX-f"])

    bvecvx_cf = dev_msig.rari.ftoken_get_cf(registry.eth.rari["fbveCVX-22"])

    dev_msig.rari.set_market_supply_caps(
        [registry.eth.rari["fbveCVX-22"]], [Decimal(single_side_liq * bvecvx_cf)]
    )

    dev_msig.post_safe_tx()