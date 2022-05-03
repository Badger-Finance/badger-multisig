from great_ape_safe.ape_api.helpers.balancer.util import *
from decimal import Decimal


# https://github.com/balancer-labs/balpy/blob/a907f7b984f4e3ba3460a1ef064003d95da5e884/balpy/balancerv2cad/src/balancerv2cad/WeightedMath.py#L74
def calc_bpt_out_given_exact_tokens_in(
    pool, reserves, amounts_in,
):

    reserves = [Decimal(x) for x in reserves]
    amounts_in = [Decimal(x) for x in amounts_in]
    normalized_weights = [Decimal(x / 1e18) for x in pool.getNormalizedWeights()]
    bptTotalSupply = Decimal(pool.totalSupply())
    swap_fee = Decimal(pool.getSwapFeePercentage() / 1e18)

    balance_ratios_with_fee = [None] * len(amounts_in)
    invariant_ratio_with_fees = 0
    for i in range(len(reserves)):
        balance_ratios_with_fee[i] = divDown((reserves[i] + amounts_in[i]), reserves[i])
        invariant_ratio_with_fees = mulDown((invariant_ratio_with_fees + balance_ratios_with_fee[i]), normalized_weights[i]) #.add(balance_ratios_with_fee[i].mulDown(normalized_weights[i]));

    invariant_ratio = Decimal(1)
    for i in range(len(reserves)):
        amount_in_without_fee = None

        if(balance_ratios_with_fee[i] > invariant_ratio_with_fees):
            non_taxable_amount = mulDown(reserves[i], (invariant_ratio - Decimal(1)))
            taxable_amount = amounts_in[i] - non_taxable_amount
            amount_in_without_fee = non_taxable_amount + (mulDown(taxable_amount, Decimal(1) - swap_fee))
        else:
            amount_in_without_fee = amounts_in[i]


        balance_ratio = divDown((reserves[i] + amount_in_without_fee), reserves[i])
        invariant_ratio = mulDown(invariant_ratio, (powDown(balance_ratio, normalized_weights[i])))

    if invariant_ratio >= 1:
        return mulDown(bptTotalSupply, (invariant_ratio - Decimal(1)))
    else:
        return 0


def calc_tokens_out_given_exact_bpt_in(
        pool,
        reserves,
        bpt_amount_in,
    ):
        total_bpt = Decimal(pool.totalSupply())
        bpt_ratio = divDown(bpt_amount_in, total_bpt)
        amounts_out = [None] * len(reserves)
        for i in range(len(reserves)):
            amounts_out[i] = mulDown(reserves[i], bpt_ratio)
        return amounts_out
