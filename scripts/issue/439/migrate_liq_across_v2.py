from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import accounts

# not sure how big this figure should be based on the time from posting to signing
# amount available to wd may vary from others lps migrating
SAFE_WD_AMOUNT_TILL_SIGN = 10e18


def main(sim=False):
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    a_badger_lp = safe.contract(registry.eth.treasury_tokens.aBADGER)
    badger = safe.contract(registry.eth.treasury_tokens.BADGER)
    hub_pool = safe.contract(registry.eth.across_bridge.hub_pool)

    safe.take_snapshot(tokens=[a_badger_lp, badger])

    exchange_rate = a_badger_lp.exchangeRateCurrent().return_value / 1e18
    liquid_reserves = a_badger_lp.liquidReserves()
    pending_reserves = a_badger_lp.pendingReserves()
    a_badger_lp_balance = a_badger_lp.balanceOf(safe)

    # https://etherscan.io/address/0x43298f9f91a4545df64748e78a2c777c580573d6#code#F1#L228
    lp_withdraw_mantisa = (
        liquid_reserves - pending_reserves
    ) / exchange_rate - SAFE_WD_AMOUNT_TILL_SIGN
    lp_withdraw_mantisa = min(lp_withdraw_mantisa, a_badger_lp_balance)
    a_badger_lp.removeLiquidity(lp_withdraw_mantisa, False)

    badger.approve(hub_pool, exchange_rate * lp_withdraw_mantisa)

    if sim:
        # force sim, in light of lack of badger whitelisting atm
        owner = accounts.at(hub_pool.owner(), force=True)
        hub_pool.enableL1TokenForLiquidityProvision(badger.address, {"from": owner})

    hub_pool.addLiquidity(badger.address, exchange_rate * lp_withdraw_mantisa)

    safe.post_safe_tx()
