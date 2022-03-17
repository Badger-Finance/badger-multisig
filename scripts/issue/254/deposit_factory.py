from brownie import Contract, Wei, interface
from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


AMOUNT_BADGER_ETH = 50_000 # to deposit into factory pool

console = Console()


def main():
    """
    deposit `AMOUNT_BADGER_ETH` and equal parts wbtc into BadgerWBTC factory pool,
    siphoning bibbtc position to fund wbtc liquidity
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    safe.init_curve()
    safe.init_curve_v2()

    bibBTC = interface.ISettV4h(registry.eth.sett_vaults.bcrvIbBTC, owner=safe.address)
    ibBTC = safe.contract(registry.eth.treasury_tokens.crvIbBTC)
    curve_lp = Contract(registry.eth.treasury_tokens.badgerWBTC_f)
    curve_pool = Contract(registry.eth.crv_factory_pools.badgerWBTC_f)
    wbtc = interface.ERC20(registry.eth.treasury_tokens.WBTC)
    badger = interface.ERC20(registry.eth.treasury_tokens.BADGER)

    safe.take_snapshot(tokens=[badger, wbtc, curve_lp.address, bibBTC.address, ibBTC.address])

    assert badger.balanceOf(safe) >= AMOUNT_BADGER_ETH * 10 ** badger.decimals()

    # get amounts to deposit into factory pool
    badger_amount = AMOUNT_BADGER_ETH * 10**badger.decimals()
    badger_per_wbtc = curve_pool.price_oracle() / 10 ** wbtc.decimals()
    wbtc_amount = badger_amount / badger_per_wbtc

    console.print('wBTC needed:', wbtc_amount / 10 ** wbtc.decimals())
    console.print('wBTC have:', wbtc.balanceOf(safe) / 10 ** wbtc.decimals())

    amount_to_withdraw = (wbtc_amount / 10**wbtc.decimals()) - (wbtc.balanceOf(safe) / 10**wbtc.decimals())
    bibBTC.withdraw(Wei(f'{amount_to_withdraw} ether'))

    # zap curve lp to wbtc for deposit
    safe.curve.withdraw_to_one_coin_zapper(
        registry.eth.curve.zap_sbtc,
        registry.eth.crv_pools.crvSBTC,
        ibBTC,
        ibBTC.balanceOf(safe),
        wbtc,
    )

    print('bibbtc position yields:', wbtc.balanceOf(safe) / 10 ** wbtc.decimals(), 'wBTC')

    safe.curve_v2.deposit(curve_lp, [badger_amount, wbtc_amount])
    console.print('oracle:', curve_pool.price_oracle() / 1e18)
    console.print('scale:', curve_pool.price_scale() / 1e18)

    safe.print_snapshot()

    safe.post_safe_tx(skip_preview=True)
