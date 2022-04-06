import json
import os
from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main(msig="techops_multisig", token_bridge="CRV", batchNum=0, index=0):
    safe = GreatApeSafe(registry.eth.badger_wallets[msig])
    outbox = interface.IOutbox(registry.eth.arbitrum.outbox, owner=safe.address)

    safe.take_snapshot(tokens=[registry.eth.treasury_tokens[token_bridge]])

    path = os.path.dirname(os.path.realpath(__file__)) + "/json_withdrawal_payload/"
    filename = f"batchNum_{batchNum}_index_{index}.json"
    with open(path + filename) as f:
        payload = json.load(f)
        # https://etherscan.io/address/0x8fda3500ea1f8c6790ce5ed482da23337b3e2a5f#code#F1#L148
        outbox.executeTransaction(
            batchNum,
            payload["proof"],
            payload["path"],
            payload["l2Sender"],
            payload["l1Dest"],
            payload["l2Block"],
            payload["l1Block"],
            payload["timestamp"],
            payload["amount"],
            payload["calldataForL1"],
        )

    safe.post_safe_tx()
