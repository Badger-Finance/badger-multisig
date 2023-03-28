import requests
import os


cg_key = os.getenv("COINGECKO_API_KEY")
if cg_key:
    headers = {"x-cg-pro-api-key": cg_key}
    cg_api_url = "https://pro-api.coingecko.com/api/v3/"
else:
    headers = {}
    cg_api_url = "https://api.coingecko.com/api/v3/"


def get_cg_price(address):
    res = requests.get(
        cg_api_url + "simple/token_price/ethereum",
        headers=headers,
        params={"contract_addresses": address, "vs_currencies": "usd"},
    )
    res.raise_for_status()

    return res.json()[address.lower()]["usd"]
