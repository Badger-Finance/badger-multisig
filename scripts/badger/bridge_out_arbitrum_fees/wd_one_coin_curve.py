from brownie import interface
from helpers.addresses import registry
from great_ape_safe import GreatApeSafe

# curve lp targets
curve_target_wd = [
    "crvRenBTC",
    "crvTricrypto"
    ]

SLIPPAGE_THRESHOLD = 0.1


def main():
    safe = GreatApeSafe(registry.arbitrum.badger_wallets.dev_multisig)
    safe.take_snapshot([registry.arbitrum.treasury_tokens.WBTC])

    for key in curve_target_wd:
        lp_token = interface.IERC20(registry.arbitrum.treasury_tokens[key], owner=safe)

        pool = (
            interface.ICurvePoolV2(registry.arbitrum.crv_3_pools[key], owner=safe.address)
            if "Tricrypto" in key
            else interface.ICurvePool(registry.arbitrum.crv_pools[key], owner=safe.address)
        )

        lp_token_balance = lp_token.balanceOf(safe)

        coin_index = 1 if "Tricrypto" in key else 0

        min_withdraw_wbtc = pool.calc_withdraw_one_coin(lp_token_balance, coin_index)

        pool.remove_liquidity_one_coin(
            lp_token_balance, coin_index, min_withdraw_wbtc * (1 - SLIPPAGE_THRESHOLD)
        )

        safe.print_snapshot()
        safe.post_safe_tx()
