from brownie import interface, Wei
from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

TOKEN = interface.ICurveLP(registry.eth.treasury_tokens.badgerWBTC_f)
POOL = interface.ICurvePoolV2(registry.eth.crv_factory_pools.badgerWBTC_f)
WBTC = interface.ERC20(registry.eth.treasury_tokens.WBTC)
BADGER = interface.ERC20(registry.eth.treasury_tokens.BADGER)


AMOUNT_BADGER_ETH = 5000 # to deposit into factory pool

console = Console()

def print_price_data():
    oracle = POOL.price_oracle() / 1e18
    scale = POOL.price_scale() / 1e18
    console.print(f'price oracle {oracle}\nprice scale {scale}\ndiff {abs(oracle - scale)}')

def calc_deposit_amount(badger_amount):
    badger_per_wbtc = POOL.price_oracle() / 10 ** WBTC.decimals()
    wbtc_amount = badger_amount / badger_per_wbtc
    return wbtc_amount

def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    safe.init_curve()
    safe.init_curve_v2()
    
    bcrvIbBTC = interface.ISettV4h(registry.eth.sett_vaults.bcrvIbBTC, owner=safe.address)
    crvIbBTC = safe.contract(registry.eth.treasury_tokens.crvIbBTC)
    
    safe.take_snapshot(tokens=[BADGER, WBTC, TOKEN.address, bcrvIbBTC.address, crvIbBTC.address])
    
    # get amounts to deposit into factory pool
    badger_amount = AMOUNT_BADGER_ETH * 10**BADGER.decimals()
    wbtc_amount = calc_deposit_amount(badger_amount)
    
    # withdraw from bcrvIbBTC position for curve lp
    bcrvIbBTC.withdraw(Wei(f'{wbtc_amount / 10**WBTC.decimals()} ether'))
    
    # zap curve lp to wbtc for deposit
    safe.curve.withdraw_to_one_coin_zapper(
        registry.eth.curve.zap_sbtc,
        registry.eth.crv_pools.crvSBTC,
        crvIbBTC,
        crvIbBTC.balanceOf(safe),
        WBTC,
    )
    
    print_price_data()
    safe.curve_v2.deposit(TOKEN, [badger_amount, wbtc_amount])
    print_price_data()
    
    safe.print_snapshot()
    
    safe.post_safe_tx()
    