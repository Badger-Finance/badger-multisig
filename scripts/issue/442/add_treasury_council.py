from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


TREASURY_COUNCIL = [
    '0xFb055FecDaDf080B10c5a5bFaf7B3b70dd660547', # Jonto [T]
    '0xaF94D299a73c4545ff702E79D16d9fb1AB5BDAbF', # Dapp [S]
    '0xaC7B5f4E631b7b5638B9b41d07f1eBED30753f16', # Lipp [T]
    '0x9c8C8bcD625Ed2903823b0b60DeaB2D70B92aFd9', # Po [T]
    '0x66496eBB9d848C6A8F19612a6Dd10E09954532D0', # 1500 [T]
    '0x6c6238309f4f36dff9942e655a678bbd4ea3bc5d', # Gosuto [M]
    '0xD10617AE4Da733d79eF0371aa44cd7fa74C41f6B', # Saj [S]
    '0x96ac69183216074dd8cfa7a380e873380445eadc', # Ayush [S]
    '0x0a9af7FAba0d5DF7A8C881e1B9cd679ee07Af8A2', # Petro [M]
]


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    recursive = interface.IGnosisSafe_v1_3_0(safe.address, owner=safe.account)
    for member in TREASURY_COUNCIL:
        if recursive.isOwner(member):
            continue
        # threshold now is three, should go to five
        # ref:https://github.com/safe-global/safe-contracts/blob/da66b45ec87d2fb6da7dfd837b29eacdb9a604c5/contracts/base/OwnerManager.sol#L46-L62
        recursive.addOwnerWithThreshold(member, 5)
    safe.post_safe_tx(call_trace=True)
