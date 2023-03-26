import requests


API_URL = "https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={}&vs_currencies=usd"


def get_cg_price(contract_address):
    res = requests.get(API_URL.format(contract_address))
    res.raise_for_status()

    return res.json()[contract_address.lower()]["usd"]
