from decimal import Decimal
from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

SLIPPAGE = 0.98


def main(top_eth_mantissa=0):
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    trops.init_curve()

    # naked tokens involved
    wbtc = trops.contract(r.treasury_tokens.WBTC)

    # curve lp tokens involved
    lp_crv_sbtc = trops.contract(r.treasury_tokens.crvSBTC)
    lp_crv_wbtc = trops.contract(r.treasury_tokens.crvRenBTC)
    lp_crv_ibbtc = trops.contract(r.treasury_tokens.crvIbBTC)

    # mstable tokens involved
    hbtc_feeder_pool = trops.contract(
        r.mstable_vaults.FpMbtcHbtc, Interface=interface.IFeederPool
    )
    im_btc = trops.contract(
        r.mstable_vaults.imBTC, Interface=interface.ISavingsContractImBtc
    )

    # helpers
    mstable_unwrapper = trops.contract(im_btc.unwrapper())

    # snap tokens
    tokens = [
        wbtc,
        lp_crv_sbtc,
        lp_crv_wbtc,
        lp_crv_ibbtc,
        hbtc_feeder_pool,
        im_btc,
    ]
    trops.take_snapshot(tokens=tokens)

    # 1. Wd curve lp to `wbtc`
    trops.curve.withdraw_to_one_coin(lp_crv_sbtc, lp_crv_sbtc.balanceOf(trops), wbtc)
    trops.curve.withdraw_to_one_coin(lp_crv_wbtc, lp_crv_wbtc.balanceOf(trops), wbtc)
    trops.curve.withdraw_to_one_coin_zapper(
        r.curve.zap_sbtc,
        r.crv_pools.crvSBTC,
        lp_crv_ibbtc,
        lp_crv_ibbtc.balanceOf(trops),
        wbtc,
    )

    # 2. Reedeming and unwrap mstable tokens to `wbtc`
    # https://etherscan.io/address/0xbb128bc208c45b3dd277e001f88e1c6648060c64#code#L3260
    hbtc_feeder_pool_mantissa = hbtc_feeder_pool.balanceOf(trops)
    min_out_wbtc_from_feeder_pool = (
        hbtc_feeder_pool.getRedeemOutput(wbtc, hbtc_feeder_pool_mantissa) * SLIPPAGE
    )
    hbtc_feeder_pool.redeem(
        wbtc, hbtc_feeder_pool_mantissa, min_out_wbtc_from_feeder_pool, trops
    )

    # https://etherscan.io/address/0x9c71192da3cff149eace50b6c94bfe69d7a6e694#code#F1#L1423
    im_btc_mantissa = im_btc.balanceOf(trops)
    min_out_wbtc_from_im_btc = (
        mstable_unwrapper.getUnwrapOutput(
            True, r.treasury_tokens.mBTC, im_btc, True, wbtc, im_btc_mantissa
        )
        * SLIPPAGE
    )
    im_btc.redeemAndUnwrap(
        im_btc_mantissa,
        True,
        min_out_wbtc_from_im_btc,
        wbtc,
        trops,
        r.treasury_tokens.mBTC,
        True,
    )

    # 3. Top-up gas station
    # NOTE: not added the withdraw from `weth` since it breaks the flow of the scripts by reverting
    cast_eth_mantissa = Decimal(top_eth_mantissa)
    if cast_eth_mantissa > 0:
        trops.account.transfer(r.badger_wallets.gas_station, cast_eth_mantissa)

    trops.post_safe_tx()
