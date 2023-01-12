from math import floor
from rich.pretty import pprint


Q128 = 2 ** 128

LABELS = {
    "pool_positions": [
        "liquidity",
        "feeGrowthInside0LastX128",
        "feeGrowthInside1LastX128",
        "tokensOwed0",
        "tokensOwed1",
    ],
    "positions": [
        "nonce",
        "operator",
        "token0",
        "token1",
        "fee",
        "tickLower",
        "tickUpper",
        "liquidity",
        "feeGrowthInside0LastX128",
        "feeGrowthInside1LastX128",
        "tokensOwed0",
        "tokensOwed1",
    ],
    "ticks": [
        "liquidityGross",
        "liquidityNet",
        "feeGrowthOutside0X128",
        "feeGrowthOutside1X128",
        "tickCumulativeOutside",
        "secondsPerLiquidityOutsideX128",
        "secondsOutside",
        "initialized",
    ],
}


def print_position(nfp, position_id):
    position_info = nfp.positions(position_id)

    position = dict(zip(LABELS["positions"], position_info))
    pprint(position)

    return position_info


def calc_accum_fees(feeGrowthInsideX128, feeGrowthInsideLastX128, liquidity):
    # https://github.com/Uniswap/v3-core/blob/c05a0e2c8c08c460fb4d05cfdda30b3ad8deeaac/contracts/libraries/Position.sol#L60-L76
    return floor((feeGrowthInsideX128 - feeGrowthInsideLastX128) * liquidity / Q128)


def calc_all_accum_fees(nfp, v3_pool_obj, position_id):
    """given a uni_v3 nfp manager, pool and position id, calculate its
    accumulated fees expressed per underlying asset"""

    position = dict(zip(LABELS["positions"], nfp.positions(position_id)))

    lower = position["tickLower"]
    upper = position["tickUpper"]

    ticks_lower = dict(zip(LABELS["ticks"], v3_pool_obj.ticks(lower)))
    ticks_upper = dict(zip(LABELS["ticks"], v3_pool_obj.ticks(upper)))

    global0 = v3_pool_obj.feeGrowthGlobal0X128()
    global1 = v3_pool_obj.feeGrowthGlobal1X128()

    outside_lower0 = ticks_lower["feeGrowthOutside0X128"]
    outside_lower1 = ticks_lower["feeGrowthOutside1X128"]

    outside_upper0 = ticks_upper["feeGrowthOutside0X128"]
    outside_upper1 = ticks_upper["feeGrowthOutside1X128"]

    inside0 = global0 - outside_lower0 - outside_upper0
    inside1 = global1 - outside_lower1 - outside_upper1

    last0 = position["feeGrowthInside0LastX128"]
    last1 = position["feeGrowthInside1LastX128"]

    return (
        calc_accum_fees(inside0, last0, position["liquidity"]),
        calc_accum_fees(inside1, last1, position["liquidity"]),
    )
