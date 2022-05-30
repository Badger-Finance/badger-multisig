import requests
import json
import time

from eth_account import messages
from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

SNAPSHOT_VOTE_RELAYER = "https://snapshot-relayer.herokuapp.com/api/message"

SNAPSHOT_DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://snapshot.org/",
}


def main(proposal="QmSwrVFfQkgmvRiL2qUssk6XfGjoQs4tTRQPsrJyqCbtbR", choice=2):
    test_msig = GreatApeSafe(registry.eth.badger_wallets.test_multisig_v1_3)

    sign_message_lib = interface.ISignMessageLib(
        registry.eth.gnosis.sign_message_lib, owner=test_msig.address
    )

    payload = {
        "version": "0.1.3",
        "timestamp": str(int(time.time())),
        "space": "cvx.eth",
        "type": "vote",
        "payload": {
            "proposal": proposal,
            "choice": choice,  # json.dumps(choice_json, separators=(",", ":")),
            "metadata": json.dumps({}),
        },
    }

    payload_stringify = json.dumps(payload, separators=(",", ":"))

    hash = messages.defunct_hash_message(text=payload_stringify)

    tx_data = sign_message_lib.signMessage.encode_input(hash)

    safe_tx = test_msig.build_multisig_tx(
        to=registry.eth.gnosis.sign_message_lib, value=0, data=tx_data, operation=1
    )

    # notify relayer to watch for this tx to be mined so it is included in the snapshot proposal
    # https://github.com/snapshot-labs/snapshot-relayer/blob/7b656d204ad78fc9c06cedafcb4288aa47775adc/src/api.ts#L36
    response = requests.post(
        SNAPSHOT_VOTE_RELAYER,
        headers=SNAPSHOT_DEFAULT_HEADERS,
        data=json.dumps(
            {
                "address": test_msig.address,
                "msg": json.dumps(payload, separators=(",", ":")),
                "sig": "0x",
            },
            separators=(",", ":"),
        ),
    )
    if not response.ok:
        print(f"Error notifying relayer: {response.text}")
    else:
        response_id = response.text
        print(f"Response ID: {response_id}")
        assert hash.hex() in response_id

    test_msig.post_safe_tx(safe_tx_arg=safe_tx, skip_preview=True)
