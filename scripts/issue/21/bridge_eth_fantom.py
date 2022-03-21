from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


CHAIN_ID_ORIGIN = 1
CHAIN_ID_DEST = 250
WETH_MANTISSA = .001e18


def main():
    """
    bridge .001 eth over to the fantom techops msig
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    safe.init_anyswap()
    info = safe.anyswap.get_token_bridge_info(
        registry.eth.treasury_tokens.WETH, CHAIN_ID_ORIGIN
    )

    router = interface.IAnyswapV6Router(info['router'], owner=safe.account)
    # info['routerABI'] determines exact (func) signature
    router.anySwapOutNative['address,address,uint256'](
        info['anyToken']['address'],
        registry.ftm.badger_wallets.techops_multisig,
        CHAIN_ID_DEST,
        {'value': WETH_MANTISSA}
    )

    safe.post_safe_tx(call_trace=True)

    # track bridging status at:
    # https://bridgeapi.anyswap.exchange/v2/history/details?params={tx_hash}
