import requests


class Anyswap:
    def __init__(self, safe):
        self.safe = safe

    api_url = "https://bridgeapi.anyswap.exchange/v3/serverinfoV3"

    def get_token_bridge_info(self, token_addr_src, chain_id_origin):
        # https://github.com/anyswap/CrossChain-Router/wiki/How-to-integrate-AnySwap-Router
        params = {"chainId": chain_id_origin, "version": "all"}
        r = requests.get(self.api_url, params=params).json()
        for version in r.keys():
            try:
                info = r[version][token_addr_src.lower()]
                return info
            except KeyError:
                continue
