import requests
from pprint import pprint

from brownie import Wei

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


FANTOM_CHAIN_ID = 250
ETH_MANTISSA = 1 * 1e18


def main():
    """
    bridge 1 eth over to the fantom msig
    """

    techops = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)

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

    # in case of ether:
    techops.account.transfer(dest, ETH_MANTISSA)

    # if ERC20; procedure is different
    # erc20.transfer(dest, ERC20_MANTISSA)

    techops.post_safe_tx(post=False)
