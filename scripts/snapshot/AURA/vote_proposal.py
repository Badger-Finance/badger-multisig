import requests
import json
import time

from eth_account import messages
from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# Relayer endpoint
SNAPSHOT_VOTE_RELAYER = "https://relayer.snapshot.org/api/message"

SNAPSHOT_DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://snapshot.org/",
}

# Snapshot url & query
SNAPSHOT_SUBGRAPH = "https://hub.snapshot.org/graphql?"
PROPOSAL_QUERY = """
        query($proposal_id: String) {
          proposal(id: $proposal_id) {
            choices
          }
        }
        """

# Currently is static, but we could add in the future args to be introduce in the cli for weights and targets
GAUGE_TARGET = "80/20 BADGER/WBTC"
VOTE_WEIGHT = 1

# UPDATE: introduce proposal ID to cast vote
def main(
    proposal_id="0x515649bddfb0e0d637745e8654616b03b371bb444f90f327064e7eee6052aff8",
):
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)

    sign_message_lib = interface.ISignMessageLib(
        r.gnosis.sign_message_lib, owner=voter.address
    )

    # given a new proposal, find index of 80badger_20wbtc gauge
    response = requests.post(
        SNAPSHOT_SUBGRAPH,
        json={"query": PROPOSAL_QUERY, "variables": {"proposal_id": proposal_id}},
    ).json()
    choices = response["data"]["proposal"]["choices"]
    # choices in snap starts on "1"
    target_index = str(choices.index(GAUGE_TARGET) + 1)

    choice_json = {target_index: VOTE_WEIGHT}

    payload = {
        "version": "0.1.3",
        "timestamp": str(int(time.time())),
        "space": "aurafinance.eth",
        "type": "vote",
        "payload": {
            "proposal": proposal_id,
            "choice": json.dumps(choice_json, separators=(",", ":")),
            "metadata": json.dumps({}),
        },
    }

    payload_stringify = json.dumps(payload, separators=(",", ":"))

    hash = messages.defunct_hash_message(text=payload_stringify)

    tx_data = sign_message_lib.signMessage.encode_input(hash)

    safe_tx = voter.build_multisig_tx(
        to=r.gnosis.sign_message_lib, value=0, data=tx_data, operation=1
    )

    # notify relayer to watch for this tx to be mined so it is included in the snapshot proposal
    # https://github.com/snapshot-labs/snapshot-relayer/blob/7b656d204ad78fc9c06cedafcb4288aa47775adc/src/api.ts#L36
    response = requests.post(
        SNAPSHOT_VOTE_RELAYER,
        headers=SNAPSHOT_DEFAULT_HEADERS,
        data=json.dumps(
            {
                "address": voter.address,
                "msg": payload_stringify,
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

    voter.post_safe_tx(safe_tx=safe_tx, skip_preview=True)
