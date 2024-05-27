from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import interface

STETH = r.treasury_tokens.STETH
WSTETH = r.treasury_tokens.WSTETH
GAUGE = r.crv_gauges.ebtc_wsteth_gauge

TROPS = r.badger_wallets.treasury_ops_multisig

MONTH = 60 * 60 * 24 * 7 * 4 # Epoch

def main(amount=0, epoch=MONTH, use_wsteth=True):
    """
    Deposit stETH or wstETH into the eBTC/wstETH Curve gauge for a given epoch
    
    Args:
        amount (int): Decimal amount of stETH or wstETH to deposit
        epoch (int): Epoch length to deposit the amount, default 1 month
        use_wsteth (bool): Use wstETH instead of stETH
    """
    safe = GreatApeSafe(TROPS)
    gauge = safe.contract(GAUGE, Interface=interface.ILiquidityGaugeV6)
    amount = int(float(amount) * 1e18)

    if use_wsteth:
        token = safe.contract(WSTETH)
    else:
        token = safe.contract(STETH)

    # 1. Approve amount
    token.approve(GAUGE, amount)

    # 2. Deposit amount
    gauge.deposit_reward_token(token.address, amount, epoch)

    # 3. Confirm deposit
    print(gauge.reward_data(token))

    safe.post_safe_tx()