from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


SLIPPAGE = 0.995


def main():
    """
    send all of dev msig's $wbtc to work on the farm
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    wbtc = safe.contract(registry.eth.treasury_tokens.WBTC)
    crvibbtc = safe.contract(registry.eth.crv_pools.crvIbBTC)
    zap = safe.contract(registry.eth.curve.zap_ibbtc)
    bcrvibbtc = safe.contract(registry.eth.sett_vaults.bcrvIbBTC)

    safe.take_snapshot(tokens=[wbtc.address, crvibbtc.address, bcrvibbtc.address])

    # first step is to deposit into the curve ibbtc pool
    to_deposit = wbtc.balanceOf(safe)
    expected = zap.calc_token_amount(crvibbtc, [0, 0, to_deposit, 0], 1)
    wbtc.approve(zap, to_deposit)
    zap.add_liquidity(crvibbtc, [0, 0, to_deposit, 0], expected * SLIPPAGE)

    # then deposit the curve lp token into the badger sett
    to_deposit = crvibbtc.balanceOf(safe) * SLIPPAGE
    crvibbtc.approve(bcrvibbtc, to_deposit)
    bcrvibbtc.deposit(to_deposit)

    # post=False prevents actually prompting for a signature to post to api
    safe.post_safe_tx(post=False)
