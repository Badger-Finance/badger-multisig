from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import Contract, interface

wbtc = Contract(registry.eth.treasury_tokens.WBTC)

RANGE_0 = 0.0000313
RANGE_1 = 0.000063

WBTC_AMOUNT = 40.82 * 10 ** wbtc.decimals()


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)

    # sett and curve lp involved
    bcrvIbBTC = interface.ISettV4h(
        registry.eth.sett_vaults.bcrvIbBTC, owner=safe.address
    )
    crvIbBTC = safe.contract(registry.eth.treasury_tokens.crvIbBTC)

    safe.take_snapshot(
        tokens=[
            registry.eth.sett_vaults.bcrvIbBTC,
            registry.eth.treasury_tokens.WBTC,
        ]
    )

    # 1. undog ibbtc sett
    bcrvIbBTC.withdraw(41e18)

    # 2. wd into wbtc
    safe.init_curve()

    safe.curve.withdraw_to_one_coin_zapper(
        registry.eth.curve.zap_sbtc,
        registry.eth.crv_pools.crvSBTC,
        crvIbBTC,
        crvIbBTC.balanceOf(safe),
        wbtc,
    )

    # 3. mint nft
    safe.init_uni_v3()

    safe.uni_v3.mint_position(
        registry.eth.uniswap.v3pool_wbtc_badger, RANGE_0, RANGE_1, WBTC_AMOUNT, 0
    )

    safe.post_safe_tx()
