import os
from pathlib import Path
import json
from brownie import interface
from helpers.addresses import registry


def main(batchNum=0, index=0):
    node = interface.INodeInterface(registry.arbitrum.arbitrum_node)

    tx_return_values = node.lookupMessageBatchProof(batchNum, index)

    proof_hexed = [data.hex() for data in tx_return_values[0]]

    os.makedirs(
        "scripts/badger/bridge_out_arbitrum_fees/json_withdrawal_payload/",
        exist_ok=True,
    )

    tx_detail_json = Path(
        f"scripts/badger/bridge_out_arbitrum_fees/json_withdrawal_payload/batchNum_{batchNum}_index_{index}.json"
    )
    with tx_detail_json.open("w") as payload:
        txData = {
            "proof": proof_hexed,
            "path": tx_return_values[1],
            "l2Sender": tx_return_values[2],
            "l1Dest": tx_return_values[3],
            "l2Block": tx_return_values[4],
            "l1Block": tx_return_values[5],
            "timestamp": tx_return_values[6],
            "amount": tx_return_values[7],
            "calldataForL1": tx_return_values[8].hex(),
        }
        json.dump(txData, payload, indent=4, sort_keys=True)
