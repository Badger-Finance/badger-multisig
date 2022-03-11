from math import ceil

BASE = 1.0001
Q128 = 2 ** 128
Q96 = 2 ** 96
Q32 = 2 ** 32
MAXUINT256 = 2 ** 256 - 1


def maxLiquidityForAmount0(sqrtA, sqrtB, amount):
    # https://github.com/Uniswap/v3-sdk/blob/d139f73823145a5ba5d90ef2f61ff33ff02b6a92/src/utils/maxLiquidityForAmounts.ts#L32-L41
    if sqrtA > sqrtB:
        sqrtA, sqrtB = sqrtB, sqrtA

    numerator = (amount * sqrtA) * sqrtB
    denominator = Q96 * (sqrtB - sqrtA)

    return numerator / denominator


def maxLiquidityForAmount1(sqrtA, sqrtB, amount):
    # https://github.com/Uniswap/v3-sdk/blob/d139f73823145a5ba5d90ef2f61ff33ff02b6a92/src/utils/maxLiquidityForAmounts.ts#L50-L55
    if sqrtA > sqrtB:
        sqrtA, sqrtB = sqrtB, sqrtA

    numerator = amount * Q96
    denominator = sqrtB - sqrtA

    return numerator / denominator


def maxLiquidityForAmounts(sqrtCurrent, sqrtA, sqrtB, amount0, amount1):
    # https://github.com/Uniswap/v3-sdk/blob/d139f73823145a5ba5d90ef2f61ff33ff02b6a92/src/utils/maxLiquidityForAmounts.ts#L68-L91
    if sqrtCurrent <= sqrtA:
        return maxLiquidityForAmount0(sqrtA, sqrtB, amount0)
    elif sqrtCurrent < sqrtB:
        liq0 = maxLiquidityForAmount0(sqrtCurrent, sqrtB, amount0)
        liq1 = maxLiquidityForAmount1(sqrtA, sqrtCurrent, amount1)
        return liq0 if liq0 < liq1 else liq1
    else:
        return maxLiquidityForAmount1(sqrtA, sqrtB, amount1)


def getAmount0Delta(sqrtA, sqrtB, liquidity, roundUp=False):
    # https://github.com/Uniswap/v3-sdk/blob/12f3b7033bd70210a4f117b477cdaec027a436f6/src/utils/sqrtPriceMath.ts#L25-L36
    if sqrtA > sqrtB:
        sqrtA, sqrtB = sqrtB, sqrtA

    shift_liquidity = liquidity * (1 << 96)
    sqrt_substraction = sqrtB - sqrtA

    numerator = (shift_liquidity * sqrt_substraction) / sqrtB

    return ceil(numerator / sqrtA) if roundUp else numerator / sqrtA


def getAmount1Delta(sqrtA, sqrtB, liquidity, roundUp=False):
    # https://github.com/Uniswap/v3-sdk/blob/12f3b7033bd70210a4f117b477cdaec027a436f6/src/utils/sqrtPriceMath.ts#L38-L46
    if sqrtA > sqrtB:
        sqrtA, sqrtB = sqrtB, sqrtA

    numerator = liquidity * (sqrtB - sqrtA)
    denominator = Q96

    return ceil(numerator / denominator) if roundUp else numerator / denominator


def getAmountsForLiquidity(sqrtCurrent, sqrtA, sqrtB, liquidity):
    # https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/LiquidityAmounts.sol#L120
    if sqrtA > sqrtB:
        sqrtA, sqrtB = sqrtB, sqrtA

    amount0 = 0
    amount1 = 0

    if sqrtCurrent < sqrtA:
        amount0 = getAmount0Delta(sqrtA, sqrtB, liquidity)
    elif sqrtCurrent < sqrtB:
        amount0 = getAmount0Delta(sqrtCurrent, sqrtB, liquidity)
        amount1 = getAmount1Delta(sqrtA, sqrtCurrent, liquidity)
    else:
        amount1 = getAmount1Delta(sqrtA, sqrtB, liquidity)

    return amount0, amount1


# https://github.com/Balt2/Uniswapv3Research/blob/main/SqrtPriceMath.py
def rshift(val, n):
    return (val) >> n


def mulShift(val, mulBy):
    return rshift(val * mulBy, 128)


def getSqrtRatioAtTick(tick):
    absTick = abs(tick)
    ratio = (
        0xFFFCB933BD6FAD37AA2D162D1A594001
        if ((absTick & 0x1) != 0)
        else 0x100000000000000000000000000000000
    )
    if (absTick & 0x2) != 0:
        ratio = mulShift(ratio, 0xFFF97272373D413259A46990580E213A)
    if (absTick & 0x4) != 0:
        ratio = mulShift(ratio, 0xFFF2E50F5F656932EF12357CF3C7FDCC)
    if (absTick & 0x8) != 0:
        ratio = mulShift(ratio, 0xFFE5CACA7E10E4E61C3624EAA0941CD0)
    if (absTick & 0x10) != 0:
        ratio = mulShift(ratio, 0xFFCB9843D60F6159C9DB58835C926644)
    if (absTick & 0x20) != 0:
        ratio = mulShift(ratio, 0xFF973B41FA98C081472E6896DFB254C0)
    if (absTick & 0x40) != 0:
        ratio = mulShift(ratio, 0xFF2EA16466C96A3843EC78B326B52861)
    if (absTick & 0x80) != 0:
        ratio = mulShift(ratio, 0xFE5DEE046A99A2A811C461F1969C3053)
    if (absTick & 0x100) != 0:
        ratio = mulShift(ratio, 0xFCBE86C7900A88AEDCFFC83B479AA3A4)
    if (absTick & 0x200) != 0:
        ratio = mulShift(ratio, 0xF987A7253AC413176F2B074CF7815E54)
    if (absTick & 0x400) != 0:
        ratio = mulShift(ratio, 0xF3392B0822B70005940C7A398E4B70F3)
    if (absTick & 0x800) != 0:
        ratio = mulShift(ratio, 0xE7159475A2C29B7443B29C7FA6E889D9)
    if (absTick & 0x1000) != 0:
        ratio = mulShift(ratio, 0xD097F3BDFD2022B8845AD8F792AA5825)
    if (absTick & 0x2000) != 0:
        ratio = mulShift(ratio, 0xA9F746462D870FDF8A65DC1F90E061E5)
    if (absTick & 0x4000) != 0:
        ratio = mulShift(ratio, 0x70D869A156D2A1B890BB3DF62BAF32F7)
    if (absTick & 0x8000) != 0:
        ratio = mulShift(ratio, 0x31BE135F97D08FD981231505542FCFA6)
    if (absTick & 0x10000) != 0:
        ratio = mulShift(ratio, 0x9AA508B5B7A84E1C677DE54F3E99BC9)
    if (absTick & 0x20000) != 0:
        ratio = mulShift(ratio, 0x5D6AF8DEDB81196699C329225EE604)
    if (absTick & 0x40000) != 0:
        ratio = mulShift(ratio, 0x2216E584F5FA1EA926041BEDFE98)
    if (absTick & 0x80000) != 0:
        ratio = mulShift(ratio, 0x48A170391F7DC42444E8FA2)

    if tick > 0:
        ratio = MAXUINT256 / ratio

    if ratio % Q32 > 0:
        return ratio / Q32 + 1
    else:
        return ratio / Q32
