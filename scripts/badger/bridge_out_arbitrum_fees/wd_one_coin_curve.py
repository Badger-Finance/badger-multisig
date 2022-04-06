from rich.console import Console
from brownie import interface, accounts
from helpers.addresses import registry

CONSOLE = Console()

# curve lp targets
curve_target_wd = ["crvRenBTC", "crvTricrypto"]

SLIPPAGE_THRESHOLD = 0.1

ACCOUNT_TO_LOAD = ""


def main(broadcast="true"):
    dev = accounts.load(ACCOUNT_TO_LOAD)

    safe = interface.IMultisigWalletWithDailyLimit(
        registry.arbitrum.badger_wallets.dev_multisig_deprecated
    )

    for key in curve_target_wd:
        lp_token = interface.IERC20(registry.arbitrum.treasury_tokens[f"{key}"])

        pool = (
            interface.ICurvePoolV2(registry.arbitrum.crv_3_pools[f"{key}"])
            if "Tricrypto" in key
            else interface.ICurvePool(registry.arbitrum.crv_pools[f"{key}"])
        )

        lp_token_balance = lp_token.balanceOf(safe)

        coin_index = 1 if "Tricrypto" in key else 0

        min_withdraw_wbtc = pool.calc_withdraw_one_coin(lp_token_balance, coin_index)

        calldata = pool.remove_liquidity_one_coin.encode_input(
            lp_token_balance, coin_index, min_withdraw_wbtc * (1 - SLIPPAGE_THRESHOLD)
        )

        CONSOLE.print(
            f" === Calldata to wd [green]{key}[/green] into WBTC, calldata=[blue]{calldata}[/blue]. Target:[blue]{pool.address}[/blue]"
        )

        if broadcast == "true":
            safe.submitTransaction(pool.address, 0, calldata, {"from": dev})
