from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.rinkeby.badger_wallets.rinkeby_multisig)
    dai = interface.ERC20(
        registry.rinkeby.treasury_tokens.DAI, owner=safe.account
    )
    dai.transfer(safe, 1_000_000e18)
    dai.transfer(safe, 2_000_000e18)

    safe.post_safe_tx_manually()
