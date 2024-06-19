from math import sqrt

from great_ape_safe import GreatApeSafe
from great_ape_safe.ape_api.helpers.uni_v3.uni_v3_sdk import BASE, Q96

from helpers.addresses import r
from brownie import interface
from rich.console import Console

C = Console()

"""
Active range: https://app.uniswap.org/pools/255188
Upper ranges (BADGER only):
    1. https://app.uniswap.org/pools/198350
    2. https://app.uniswap.org/pools/151049
    3. https://app.uniswap.org/pools/167046
"""

# Constants: active range, upper ranges and BIP parameter
ACTIVE_RANGE_NFT_ID = 255188
UPPER_RANGE_NFT_IDS = [198350, 151049, 167046]
HALF_LIQUIDITY_PCT = 0.5

safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
safe.init_uni_v3()

# tokens
badger = safe.contract(r.treasury_tokens.BADGER)
ebtc = safe.contract(r.treasury_tokens.EBTC)
wbtc = safe.contract(r.treasury_tokens.WBTC)

# decimals for calculating tick to prices ratio
decimals_diff = badger.decimals() - wbtc.decimals()

# Scope:
# 1. Migrates active range from BADGER/WBTC to BADGER/EBTC, partially (50%)
# 2. Migrates upper ranges from BADGER/WBTC to BADGER/EBTC, partially (50%)
def main():
    # existing univ3 pool
    univ3_badger_wbtc = safe.contract(r.uniswap.v3pool_wbtc_badger)

    # snap
    safe.take_snapshot(tokens=[badger, ebtc, wbtc])

    # 1. Withdraw 50% of active range
    prev_badger_balance = badger.balanceOf(safe)
    prev_wbtc_balance = wbtc.balanceOf(safe)

    safe.uni_v3.burn_token_id(ACTIVE_RANGE_NFT_ID, HALF_LIQUIDITY_PCT)

    # 2. Buy eBTC with withdrawn WBTC funds
    wbtc_sell_amount = wbtc.balanceOf(safe) - prev_wbtc_balance
    C.print(f"[green]WBTC to sell for eBTC: {wbtc_sell_amount}[/green]")
    ebtc_balance = safe.uni_v3.swap([wbtc, ebtc], wbtc_sell_amount)

    # 3. Pool creation (BADGER/EBTC) and initilization
    pool_ebtc_badger_address = safe.uni_v3.factory.createPool(
        ebtc, badger, univ3_badger_wbtc.fee()
    ).return_value
    C.print(f"[green]Pool address is: {pool_ebtc_badger_address}[/green]")

    ebtc_badger_pool = interface.IUniswapV3Pool(
        pool_ebtc_badger_address, owner=safe.account
    )

    # NOTE: token0 will be BADGER
    # ref: https://github.com/Uniswap/v3-core/blob/main/contracts/UniswapV3Factory.sol#L41
    C.print(f"[green]Token0 is: {ebtc_badger_pool.token0()}[/green]")
    C.print(f"[green]Token1 is: {ebtc_badger_pool.token1()}\n[/green]")

    # aim to initialize at same tick as existing badger/wbtc pool
    _, current_tick_badger_wbtc_pool, _, _, _, _, _ = univ3_badger_wbtc.slot0()
    C.print(
        f"[green]Current badger/wbtc pool tick: {current_tick_badger_wbtc_pool}\n[/green]"
    )
    current_price_pool_badger_wbtc = (
        1 / (BASE ** current_tick_badger_wbtc_pool) * 10 ** decimals_diff
    )
    C.print(f"[green]Current price: {current_price_pool_badger_wbtc}\n[/green]")

    sqrt_price_x_96 = sqrt(current_price_pool_badger_wbtc) * Q96
    ebtc_badger_pool.initialize(sqrt_price_x_96)
    _, current_tick_badger_ebtc_pool, _, _, _, _, _ = ebtc_badger_pool.slot0()
    C.print(
        f"[green]Current badger/ebtc pool tick: {current_tick_badger_ebtc_pool}\n[/green]"
    )

    # 4. Create/mirror active range BADGER/EBTC
    active_range_0, active_range_1 = _range_prices(
        safe.uni_v3.nonfungible_position_manager, ACTIVE_RANGE_NFT_ID, decimals_diff
    )

    badger_to_deposit_active_range = (
        badger.balanceOf(safe.address) - prev_badger_balance
    )
    C.print(
        f"[green]BADGER amount to deposit in active range: {badger_to_deposit_active_range}[/green]"
    )

    safe.uni_v3.mint_position(
        pool_ebtc_badger_address,
        active_range_0,
        active_range_1,
        badger_to_deposit_active_range,
        ebtc_balance,
    )

    # 5. Migrate upper ranges
    for nft_id in UPPER_RANGE_NFT_IDS:
        range_0, range_1 = _range_prices(
            safe.uni_v3.nonfungible_position_manager, nft_id, decimals_diff
        )

        badger_bal_before = badger.balanceOf(safe.address)
        safe.uni_v3.burn_token_id(nft_id, HALF_LIQUIDITY_PCT)

        # NOTE: ensure clean BADGER approval. Force to set back to zero due to its nature
        # otherwise may revert in the internal approval of the class
        badger.approve(safe.uni_v3.nonfungible_position_manager.address, 0)

        # NOTE: deposit the difference only. should be theoretically 100% BADGER nft's
        safe.uni_v3.mint_position(
            pool_ebtc_badger_address,
            range_0,
            range_1,
            badger.balanceOf(safe.address) - badger_bal_before,
            0,  # should be theoretically 0 eBTC
        )

    safe.post_safe_tx()


def _range_prices(position_manager, token_id, decimals_diff):
    C.print(f"[green]Inspecting ticks for token id {token_id}...[/green]")
    position = position_manager.positions(token_id)

    tick_lower = position["tickLower"]
    tick_upper = position["tickUpper"]
    C.print(f"[green]tickLower: {tick_lower}[/green]")
    C.print(f"[green]tickLower: {tick_upper}\n[/green]")

    range_0 = 1 / (BASE ** tick_lower) * 10 ** decimals_diff
    range_1 = 1 / (BASE ** tick_upper) * 10 ** decimals_diff
    C.print(f"[green]range_0: {range_0}[/green]")
    C.print(f"[green]range_1: {range_1}\n[/green]")

    return range_0, range_1
