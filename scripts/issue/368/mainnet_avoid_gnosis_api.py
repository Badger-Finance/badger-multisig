from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.test_multisig)
    weth = interface.ERC20(
        registry.eth.treasury_tokens.WETH, owner=safe.account
    )
    weth.transfer(safe, .0001e18)
    weth.transfer(safe, .0001e18)

    safe.post_safe_tx_manually()
