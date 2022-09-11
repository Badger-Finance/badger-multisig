from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


SAFE = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
WBTC = SAFE.contract(registry.eth.treasury_tokens.WBTC)
AWBTC = SAFE.contract(registry.eth.treasury_tokens.aWBTC)
USDC = SAFE.contract(registry.eth.treasury_tokens.USDC)


def lever_up():
    SAFE.init_aave()
    SAFE.take_snapshot([WBTC, AWBTC, USDC])

    SAFE.aave.deposit(WBTC, 1e8)
    SAFE.aave.lever_up(WBTC, USDC, 0.5)

    SAFE.post_safe_tx()


def delever():
    SAFE.init_aave()
    SAFE.take_snapshot([WBTC, AWBTC, USDC])

    SAFE.aave.delever(WBTC, USDC)
    SAFE.aave.withdraw_all(WBTC)

    SAFE.post_safe_tx()
