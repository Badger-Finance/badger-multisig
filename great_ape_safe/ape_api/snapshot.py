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

        self.vote_relayer = "https://relayer.snapshot.org/api/message"
        self.subgraph = "https://hub.snapshot.org/graphql?"
        self.proposal_query = """
            query($proposal_id: String) {
                proposal(id: $proposal_id) {
                    choices
                    state
                    type
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
        self.proposal_data = self._get_proposal_data(self.proposal_id)
    
    
    def handle_response(self, response):
        if not response.ok:
            console.print(f"Error: {response.text}")
            raise


    def _get_proposal_data(self, proposal_id):
        # query subgraph for proposal data
        response = requests.post(
            self.subgraph,
            json={"query": self.proposal_query, "variables": {"proposal_id": proposal_id}},
        )

        self.handle_response(response)
        return response.json()["data"]["proposal"]


    def show_proposal_choices(self):
        # external helper method to view proposal choices
        choices = self.proposal_data["choices"]
        console.print(f"Choices for proposal {self.proposal_id}: {choices}")


    def create_payload_hash(
            self,
            payload=None, 
            timestamp=None, 
            proposal=None, 
            choice=None, 
            version="0.1.3", 
            type="vote",
            metadata=""
        ):
        # helper method to create message hash from payload and output to console
        # can be used externally to verify generated hash
        if not payload:
            assert all([timestamp, proposal, choice])
            payload = {
                "version": version,
                "timestamp": timestamp,
                "space": self.proposal_data["space"]["id"],
                "type": type,
                "payload": {
                    "proposal": proposal,
                    "choice": choice,
                    "metadata": metadata,
                },
            }

        payload_stringify = json.dumps(payload, separators=(",", ":"))
        hash = messages.defunct_hash_message(text=payload_stringify)
        console.print(f"msg hash: {hash.hex()}")
        return hash, payload_stringify


    def vote_and_post(self, choice, version="0.1.3", type="vote", metadata=""):
        # given a choice, contruct payload, post to vote relayer and post safe tx
        # for single vote, pass in choice as str ex: "yes"
        # for weighted vote, pass in choice(s) as dict ex: {"80/20 BADGER/WBTC": 1}
        choices = self.proposal_data["choices"]
        space = self.proposal_data["space"]["id"]
        vote_type = self.proposal_data["type"]
        state = self.proposal_data["state"]
        is_weighted = vote_type == "weighted"

        assert state == "active", "Vote is not within proposal time window"
        assert isinstance(choice, dict if vote_type == "weighted" else str)

        if is_weighted:
            choices_index = {choices.index(k) + 1: v for k, v in choice.items()}
            choice = json.dumps(
                choices_index,
                separators=(",", ":")
            )
        else:
            choice = str(choices.index(choice) + 1)
            assert int(choice) <= len(choices) + 1, \
                "choice out of bounds"

        payload = {
            "version": version,
            "timestamp": str(int(time.time())),
            "space": space,
            "type": type,
            "payload": {
                "proposal": self.proposal_id,
                "choice": choice, # starts at 1
                "metadata": metadata,
            }
        }

        console.print("payload", payload)
        hash, payload_stringify = self.create_payload_hash(payload)

        if is_weighted:
            for choice, weight in choices_index.items():
                console.print(f"signing vote for choice {choice} with {weight * 100}% weight")
        else:
            console.print(f"signing vote for choice {choice}")

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

        self.handle_response(response)

        safe_tx = self.safe.build_multisig_tx(
            to=registry.eth.gnosis.sign_message_lib, value=0, data=tx_data, operation=1
        )

        self.safe.post_safe_tx(safe_tx=safe_tx, skip_preview=True)
