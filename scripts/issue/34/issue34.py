from brownie import interface, network
from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie_tokens import MintableForkToken

TOKEN = interface.ICurveLP(registry.eth.treasury_tokens.badgerWBTC_f)
POOL = interface.ICurvePoolV2(registry.eth.crv_factory_pools.badgerWBTC_f)

AMOUNT_BADGER_ETH = 15000 # to deposit into factory pool

console = Console()

def print_price_data():
    oracle = POOL.price_oracle() / 1e18
    scale = POOL.price_scale() / 1e18
    console.print(f'price oracle {oracle}\nprice scale {scale}\ndiff {abs(oracle - scale)}')

def calc_deposit_amount(amount):
    # calc amount wbtc to deposit, given badger amount
    return POOL.get_dy(0, 1, amount)

def main():
    
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    safe.init_curve_v2()

    if 'fork' in network.show_active():
        WBTC = MintableForkToken(registry.eth.treasury_tokens.WBTC)
        BADGER = MintableForkToken(registry.eth.treasury_tokens.BADGER)
        WBTC._mint_for_testing(safe.address, 3.5 * 10**WBTC.decimals())
        BADGER._mint_for_testing(safe.address, 15000 * 10**BADGER.decimals())
    else:
        WBTC = interface.ERC20(registry.eth.treasury_tokens.WBTC)
        BADGER = interface.ERC20(registry.eth.treasury_tokens.BADGER)
    
    safe.take_snapshot(tokens=[BADGER, WBTC])
    
    badger_amount = AMOUNT_BADGER_ETH * 10**BADGER.decimals()
    wbtc_amount = calc_deposit_amount(badger_amount)
    
    print_price_data()
    safe.curve_v2.deposit(TOKEN, [badger_amount, wbtc_amount])
    print_price_data()
    
    safe.post_safe_tx()
    