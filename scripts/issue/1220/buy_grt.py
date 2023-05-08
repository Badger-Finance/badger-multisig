from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():

    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    dai = trops.contract(r.treasury_tokens.DAI)
    grt = trops.contract(r.treasury_tokens.GRT)

    trops.init_cow(prod=True)
    trops.cow.limit_sell(
        asset_sell=dai,
        asset_buy=grt,
        mantissa_sell=15_000e18,
        mantissa_buy=100_000e18,
        destination=r.badger_wallets.techops,
    )

    trops.post_safe_tx()
