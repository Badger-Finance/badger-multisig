
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface
from eth_abi import encode_abi


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_rari()

    fbveCVX = interface.IFToken(registry.eth.rari['fbveCVX-22'], owner=safe.address)
    underlying = fbveCVX.underlying()
    comptroller = fbveCVX.comptroller()
    interest_rate_model = fbveCVX.interestRateModel()
    name = fbveCVX.name()
    symbol = fbveCVX.symbol()
    implementation = fbveCVX.implementation()


    PARAMS = [
        underlying,
            comptroller,
            interest_rate_model,
            name,
            symbol,
            implementation,
            b"\0",
            0,
            0,
    ]

    call_data = encode_abi(
        ['address', 'address', 'address', 'string', 'string', 'address', 'bytes', 'uint256', 'uint256'],
        PARAMS
        )

    safe.rari.unitroller._deployMarket(False, call_data, 0.5 * 1e18)

    safe.post_safe_tx()
