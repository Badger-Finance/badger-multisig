import json
import time

from eth_account import messages
from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

# since i delegated after proposal creation, i think we do not have vp yet showing up in this msig
def main(proposal="QmXa7do3QR6eC3v4uHzxXMS8ZwNFu9Sztf5KMPBmRpJNhe", choice=2):
    # delegated CVX vp: https://etherscan.io/tx/0xfb6e0e0564c8c40489bb2c3312e8de9169ecd791e2ffabe6fcf842d48d0b833c
    test_msig = GreatApeSafe(registry.eth.badger_wallets.test_multisig_v1_3)

    # sign_message_lib = test_msig.contract(registry.eth.gnosis.sign_message_lib)
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
            "choice": choice,
            "metadata": json.dumps({}),
        },
    }

    payload_stringify = json.dumps(payload, separators=(",", ":"))

    hash = messages.defunct_hash_message(text=payload_stringify)

    # seems like the STATICCALL calls the SignMessageLib itself, while
    # 'to' should be imo test_msig.address
    # debug internally thru `history[-1].subcalls`
    sign_message_lib.signMessage(hash)

    test_msig.post_safe_tx(skip_preview=True)
