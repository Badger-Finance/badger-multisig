import pandas as pd

from brownie import chain
from dotmap import DotMap
from web3 import Web3
import json

ADDRESSES_ETH = {
    "ebtc": {
        "placeholder":"0x0"
    },
    "ebtc_wallets": {
        "ebtc_deployer": "0xC39A1159eDd78458E7b4943fcCa45c769b0E223e",
    }
}

ADDRESSES_SEPOLIA = {
    "ebtc": {
        "collateral": "0x97BA9AA7B7DC74f7a74864A62c4fF93b2b22f015",
        "authority": "0xDcf7533497bC4baAf5beB385C82027A39B11a2f6",
        "liquidation_library": "0xFbeCFbA9B33f95C0Dc8E915D7b4ECA06E09bb67c",
        "cdp_manager": "0x4BaA1Fdf4EeA0C52a4D37ce6F64EBb51b342b348",
        "borrower_operations": "0x606bC21c399cBBA0c0d427047cDB2b50B1E05087",
        "ebtc_token": "0x2459A79d406256030d339379592ae2fF639bA324",
        "price_feed": "0x825e07ad92B2933481E63DC8eAd087EF0dB5d7Ca",
        "active_pool": "0x55F246A87E988E582b621355E952f6ac3aF5CDd2",
        "coll_surplus_pool": "0x7bc76C622A5c35c4610864a83cd7da5CB668C986",
        "sorted_cdps": "0xdA3Bb1b380C7Cfd9279dC3334F6122587C8e52A9",
        "hint_helpers": "0x52A6C2C30Eb6E3c9E8a0BF1479d8d81ad4c6fCE4",
        "fee_recipient": "0xeAB976bBE69fE936beD9D079B4f61A19be4Cb69A",
        "multi_cdp_getter": "0xE9F8c2ff6014184959b970ac7CbE7073B78C291c"
    },
    "ebtc_wallets": {
        "ebtc_deployer": "0xC39A1159eDd78458E7b4943fcCa45c769b0E223e",
    }
}


def checksum_address_dict(addresses):
    """
    convert addresses to their checksum variant taken from a (nested) dict
    """
    checksummed = {}
    for k, v in addresses.items():
        if isinstance(v, str):
            checksummed[k] = Web3.toChecksumAddress(v)
        elif isinstance(v, dict):
            checksummed[k] = checksum_address_dict(v)
        else:
            print(k, v, "formatted incorrectly")
    return checksummed


with open("helpers/chaindata.json") as chaindata:
    chain_ids = json.load(chaindata)


registry = DotMap(
    {
        "eth": checksum_address_dict(ADDRESSES_ETH),
        "sepolia": checksum_address_dict(ADDRESSES_SEPOLIA)
    }
)


def get_registry():
    try:
        if chain.id == 1:
            return registry.eth
        elif chain.id == 11155111:
            return registry.sepolia
    except:
        return registry.eth


r = get_registry()

# flatten nested dicts and invert the resulting key <-> value
# this allows for reversed lookup of an address
df = pd.json_normalize(registry, sep="_")
reverse = df.T.reset_index().set_index(0)["index"].to_dict()
