"""
To update the DIGG Median Oracle (0x058ec2Bf15011095a25670b618A129c043e2162E)
providers need to push reports. Removing the providers from the oracle prevents
the price from being updating and prevents rebasing.
"""

from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    dev = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    oracle = interface.IMedianOracle(registry.eth.oracles.oracle, owner=dev.account)

    for _ in range(oracle.providersSize()):
        oracle.removeProvider(oracle.providers(0))

    assert oracle.providersSize() == 0

    dev.post_safe_tx(call_trace=True)
