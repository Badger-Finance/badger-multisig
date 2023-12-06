from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


SAFE = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
WBTC = SAFE.contract(registry.eth.treasury_tokens.WBTC)
AWBTC = SAFE.contract(registry.eth.treasury_tokens.aWBTC)
USDC = SAFE.contract(registry.eth.treasury_tokens.USDC)

INITIAL_DEPOSIT = 5 * 10**WBTC.decimals() #Ref: https://etherscan.io/tx/0x52b76fb6f90df24eaa23d2793e3aef3d35a7f0f5ed2e95b6f8fed6f488b8c77b

# slippages
COEF = 0.95
DEADLINE = 60 * 60 * 12

def lever_up():
    SAFE.init_aave()
    SAFE.take_snapshot([WBTC, AWBTC, USDC])

    SAFE.aave.deposit(WBTC, 1e8)
    SAFE.aave.lever_up(WBTC, USDC, 0.5)

    SAFE.post_safe_tx()


def delever():
    SAFE.init_aave()
    SAFE.init_cow(True)
    SAFE.take_snapshot([WBTC, AWBTC, USDC])

    wbtc_bal_before = WBTC.balanceOf(SAFE.account)
    SAFE.aave.delever(WBTC, USDC, USDC)
    SAFE.aave.withdraw_all(WBTC)
    wbtc_bal_after = WBTC.balanceOf(SAFE.account)

    wbtc_gained = (wbtc_bal_after - wbtc_bal_before) - INITIAL_DEPOSIT
    print("wBTC Gained:", wbtc_gained)

    SAFE.cow.market_sell(
        WBTC, USDC, wbtc_gained, deadline=DEADLINE, coef=COEF
    )

    SAFE.post_safe_tx(skip_preview=True, replace_nonce=231)
