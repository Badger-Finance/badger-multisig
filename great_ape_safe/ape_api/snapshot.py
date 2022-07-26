import requests
import json
import time
from rich.console import Console

from eth_account import messages
from brownie import interface
from helpers.addresses import registry


console = Console()


class Snapshot():
    def __init__(self, safe, proposal_id):
        self.safe = safe

        self.sign_message_lib = interface.ISignMessageLib(
            registry.eth.gnosis.sign_message_lib, owner=self.safe.account
        )

        self.vote_relayer ="https://relayer.snapshot.org/api/message"
        self.subgraph = "https://hub.snapshot.org/graphql?"
        self.proposal_query = """
            query($proposal_id: String) {
                proposal(id: $proposal_id) {
                    choices
                    state
                    space {
                        id
                    }
                }
            }
        """
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Referer": "https://snapshot.org/",
        }

        self.proposal_id = proposal_id
        self.propoosal_data = self._get_proposal_data(self.proposal_id)


    def _get_proposal_data(self, proposal_id):
        # query subgraph for proposal data
        response = requests.post(
            self.subgraph,
            json={"query": self.proposal_query, "variables": {"proposal_id": proposal_id}},
        ).json()

        return response["data"]["proposal"]


    def show_proposal_choices(self):
        # external helper method to view proposal choices
        choices = self.propoosal_data['choices']
        console.print(f"Choices for proposal {self.proposal_id}: {choices}")
    

    def vote(self, choice, version="0.1.3", type="vote", metadata=""):
        # given a choice, contruct payload, send to vote relayer and return the tx data to sign message
        choices = self.propoosal_data['choices']
        choice_index = choices.index(choice)
        space = self.propoosal_data['space']['id']
        choices = self.propoosal_data['choices']

        assert choices.index(choice) <= len(choices), "choice out of bounds"

        payload = {
            "version": version,
            "timestamp": str(int(time.time())),
            "space": space,
            "type": type,
            "payload": {
                "proposal": self.proposal_id,
                "choice": str(choice_index + 1), # starts at 1
                "metadata": json.dumps({metadata}),
            }
        }

        payload_stringify = json.dumps(payload, separators=(",", ":"))
        hash = messages.defunct_hash_message(text=payload_stringify)
        tx_data = self.sign_message_lib.signMessage.encode_input(hash)

        response = requests.post(
            self.vote_relayer,
            headers=self.headers,
            data=json.dumps(
                {
                    "address": self.safe.address,
                    "msg": payload_stringify,
                    "sig": "0x",
                },
                separators=(",", ":"),
            ),
        )

        if not response.ok:
            print(f"Error notifying relayer: {response.text}")
            raise

        return self.safe.build_multisig_tx(
            to=registry.eth.gnosis.sign_message_lib, value=0, data=tx_data, operation=1
        )
