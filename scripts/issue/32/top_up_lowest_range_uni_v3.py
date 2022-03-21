from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import Wei, interface

# Targets
WD_IBBTC = 27.238487332137918
MISSING_WBTC_IN_RANGE = 27.271680860000004
TOKEN_ID = "198350"


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)

    wbtc = safe.contract(registry.eth.treasury_tokens.WBTC)
    badger = safe.contract(registry.eth.treasury_tokens.BADGER)

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

    # 1. undog exact amount for topping-up lowest range
    bcrvIbBTC.withdraw(Wei(f"{WD_IBBTC} ether"))

    # 2. wd into wbtc
    safe.init_curve()

    safe.curve.withdraw_to_one_coin_zapper(
        registry.eth.curve.zap_sbtc,
        registry.eth.crv_pools.crvSBTC,
        crvIbBTC,
        crvIbBTC.balanceOf(safe),
        wbtc,
    )

    # 3. top-up nft
    safe.init_uni_v3()

    safe.uni_v3.increase_liquidity(
        TOKEN_ID, wbtc, badger, MISSING_WBTC_IN_RANGE * 10 ** wbtc.decimals(), 0
    )

    safe.post_safe_tx(skip_preview=True)
