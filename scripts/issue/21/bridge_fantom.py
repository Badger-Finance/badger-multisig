import requests
from pprint import pprint

from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


FANTOM_CHAIN_ID = 250
WETH_MANTISSA = 1e18


def main():
    """
    bridge 1 weth over to the fantom msig
    """

    techops = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    weth = interface.IWETH9(
        registry.eth.treasury_tokens.WETH, owner=techops.account
    )

    url = f'https://bridgeapi.anyswap.exchange/v2/serverInfo/'

    def get_token_bridge_info(token_addr_src, chain_id_dest):
        resp = requests.get(url + str(chain_id_dest)).json()

        hits = []
        for label in resp.keys():
            try:
                this_addr = resp[label]['SrcToken']['ContractAddress'].lower()
            except KeyError:
                # some entries dont have `ContractAddress` apparently..
                continue
            if this_addr == token_addr_src.lower():
                hits.append(resp[label])
        assert len(hits) == 1
        return hits[0]

    info = get_token_bridge_info(
        registry.eth.treasury_tokens.WETH, FANTOM_CHAIN_ID
    )
    pprint(info)

    dest = info['SrcToken']['DcrmAddress']

    weth.deposit({'value': WETH_MANTISSA})
    weth.transfer(dest, WETH_MANTISSA)

    # on ftm? by what address? permissionless?
    # dest_token = interface.IAnyswapV5ERC20(info['DestToken']['ContractAddress'])
    # dest_token.swapin(tx_hash, account, amount)

    techops.post_safe_tx(post=False, call_trace=True)
