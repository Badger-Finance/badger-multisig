from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import Contract, accounts, chain

wbtc = Contract(registry.eth.treasury_tokens.WBTC)

RANGE_0 = 0.000063
RANGE_1 = 0.00012

WBTC_AMOUNT = 20 * 10 ** wbtc.decimals()


def main(sim="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)

    if sim == "true":
        wbtc_whale = accounts.at(
            "0x6262998Ced04146fA42253a5C0AF90CA02dfd2A3", force=True
        )
        wbtc.transfer(safe.address, WBTC_AMOUNT, {"from": wbtc_whale})
        chain.snapshot()

    safe.take_snapshot(
        tokens=[
            registry.eth.treasury_tokens.WBTC,
        ]
    )

    # mint nft
    safe.init_uni_v3()

    safe.uni_v3.positions_info()  # print general info, to get general picture from current nfts

    safe.uni_v3.mint_position(RANGE_0, RANGE_1, WBTC_AMOUNT, 0)

    safe.post_safe_tx()
