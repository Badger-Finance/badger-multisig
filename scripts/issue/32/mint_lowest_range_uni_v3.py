from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import Contract, interface

wbtc = Contract(registry.eth.treasury_tokens.WBTC)

RANGE_0 = 0.000063
RANGE_1 = 0.000125

# only 1 for minting
WBTC_AMOUNT = 1 * 10 ** wbtc.decimals()

SLIPPAGE = 0.995


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)

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
    bcrvIbBTC.withdrawAll()

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

    safe.uni_v3.positions_info()  # print general info, to get general picture from current nfts

    safe.uni_v3.mint_position(
        registry.eth.uniswap.v3pool_wbtc_badger,
        RANGE_0,
        RANGE_1,
        wbtc.balanceOf(safe) * SLIPPAGE,
        0,
    )

    safe.post_safe_tx()
