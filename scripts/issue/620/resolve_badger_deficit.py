from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    badger = interface.ERC20(registry.eth.treasury_tokens.BADGER, owner=trops.account)

    trops.take_snapshot([badger])

    # current deficit is ~198k badger + 19k badger which will be emitted between week 27 - 31
    # https://github.com/Badger-Finance/badger-multisig/issues/620#issuecomment-1177909957
    badger.transfer(registry.eth.drippers.tree_2022_q3, 223_000e18)

    trops.post_safe_tx()
