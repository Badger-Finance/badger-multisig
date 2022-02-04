from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import Contract, accounts, chain, Wei, interface

wbtc = Contract(registry.eth.treasury_tokens.WBTC)

RANGE_0 = 0.000063
RANGE_1 = 0.00012

WBTC_AMOUNT = 20 * 10 ** wbtc.decimals()

SLIPPAGE = .99

def main(sim="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)

    # sett and curve lp involved
    bcrvIbBTC = interface.ISettV4h(registry.eth.sett_vaults.bcrvIbBTC, owner=safe.address)
    crvIbBTC = safe.contract(registry.eth.treasury_tokens.crvIbBTC)
    crvSBTC = safe.contract(registry.eth.treasury_tokens.crvSBTC)

    if sim == "true":
        biibtc_whale = accounts.at(
            registry.eth.badger_wallets.treasury_vault_multisig, force=True
        )
        # the amount which will come from vault to treasury
        bcrvIbBTC.transfer(safe.address, Wei("25 ether"), {"from": biibtc_whale})
        chain.snapshot()

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

    crvIbBTC.approve(registry.eth.curve.zap_sbtc, crvIbBTC.balanceOf(safe))
    
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

    safe.uni_v3.mint_position(RANGE_0, RANGE_1, WBTC_AMOUNT, 0)

    safe.post_safe_tx()
