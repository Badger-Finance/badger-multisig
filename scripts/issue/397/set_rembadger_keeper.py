from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    dripper = interface.IEmissionsDripper(
        registry.eth.drippers.rembadger_2022_q2, owner=safe.account
    )
    dripper.setKeeper(registry.eth.badger_wallets.ops_botsquad)
    safe.post_safe_tx(call_trace=True)
