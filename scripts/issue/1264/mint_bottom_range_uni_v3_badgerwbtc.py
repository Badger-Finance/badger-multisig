from great_ape_safe import GreatApeSafe
from helpers.addresses import r


RANGE_0 = 0.000015625
RANGE_1 = 0.00003125

WBTC_AMOUNT = 28.87e8


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    wbtc = safe.contract(r.treasury_tokens.WBTC)

    safe.take_snapshot([wbtc])

    safe.init_uni_v3()

    safe.uni_v3.mint_position(
        r.uniswap.v3pool_wbtc_badger, RANGE_0, RANGE_1, WBTC_AMOUNT, 0
    )

    safe.post_safe_tx()
