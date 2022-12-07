import requests
import json
import time
from rich.console import Console

from eip712.hashing import hash_message as hash_eip712_message
from eip712.validation import validate_structured_data
from brownie import interface, web3
from helpers.addresses import registry


console = Console()


class Snapshot:
    def __init__(self, safe, proposal_id):
        self.safe = safe

        self.sign_message_lib = interface.ISignMessageLib(
            registry.eth.gnosis.sign_message_lib, owner=self.safe.account
        )
        # https://github.com/snapshot-labs/snapshot-relayer/blob/master/src/constants.json#L3
        self.vote_relayer = "https://relayer.snapshot.org/api/msg"
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
        self.domain = {
            "name": "snapshot",
            "version": "0.1.4",
        }
        # `string` proposal type: https://vote.convexfinance.com/#/proposal/bafkreihkhe75abvrfl67oz7ucxxm42mn3ofxb267z3wyzxj7rcc7e7hq3a
        self.eip_712_type = {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
            ],
            "Vote": [
                {"name": "from", "type": "address"},
                {"name": "space", "type": "string"},
                {"name": "timestamp", "type": "uint64"},
                {"name": "proposal", "type": "string"},
                {"name": "choice", "type": "string"},
                {"name": "metadata", "type": "string"},
            ],
        }
        # `bytes32` proposal type: https://vote.aura.finance/#/proposal/0x022c66d408c9bccdf4f7e514718415d2717bc22290adea71f1b5261dbeb92f3c
        self.eip_712_type_2 = {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
            ],
            "Vote": [
                {"name": "from", "type": "address"},
                {"name": "space", "type": "string"},
                {"name": "timestamp", "type": "uint64"},
                {"name": "proposal", "type": "bytes32"},
                {"name": "choice", "type": "string"},
                {"name": "reason", "type": "string"},
                {"name": "app", "type": "string"},
                {"name": "metadata", "type": "string"},
            ],
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
            json={
                "query": self.proposal_query,
                "variables": {"proposal_id": proposal_id},
            },
        )

        self.handle_response(response)
        return response.json()["data"]["proposal"]

    def show_proposal_choices(self):
        # external helper method to view proposal choices
        choices = self.proposal_data["choices"]
        console.print(f"Choices for proposal {self.proposal_id}: {choices}")

    def format_choice(self, choice):
        choices = self.proposal_data["choices"]
        if isinstance(choice, dict):
            try:
                return {str(choices.index(k) + 1): v for k, v in choice.items()}
            except ValueError:
                print(choices)
        else:
            choice = int(choices.index(choice) + 1)
            assert choice <= len(choices) + 1, "choice out of bounds"
            return choice

    def create_payload_hash(
        self,
        payload=None,
        timestamp=None,
        choice=None,
        proposal=None,
        reason="",
    ):
        # helper method to create message hash from payload and output to console
        # can be used externally to verify generated hash
        if not payload:
            assert all([timestamp, choice])

            if self.proposal_id.startswith("0x"):
                types = self.eip_712_type_2
                proposal = web3.toBytes(hexstr=self.proposal_id)
            else:
                types = self.eip_712_type
                proposal = self.proposal_id

            payload = {
                "domain": self.domain,
                "message": {
                    "from": self.safe.address,
                    "space": self.proposal_data["space"]["id"],
                    "timestamp": int(timestamp),
                    "proposal": proposal,
                    "choice": json.dumps(self.format_choice(choice)),
                    "reason": reason,
                    "app": "snapshot",
                    "metadata": json.dumps({}),
                },
                "primaryType": "Vote",
                "types": types,
            }
            
            validate_structured_data(payload)

        # https://github.com/ApeWorX/eip712/blob/main/eip712/hashing.py#L261
        hash = hash_eip712_message(payload)
        console.print(f"msg hash: {hash.hex()}")

        return hash

    def vote_and_post(self, choice, reason="", metadata=None):
        # given a choice, contruct payload, post to vote relayer and post safe tx
        # for single vote, pass in choice as str ex: "yes"
        # for weighted vote, pass in choice(s) as dict ex: {"80/20 BADGER/WBTC": 1}
        space = self.proposal_data["space"]["id"]
        vote_type = self.proposal_data["type"]
        state = self.proposal_data["state"]
        is_weighted = vote_type == "weighted"

        assert state == "active", "Vote is not within proposal time window"
        assert isinstance(choice, dict if is_weighted else str)

        choice_formatted = self.format_choice(choice)

        if self.proposal_id.startswith("0x"):
            types = self.eip_712_type_2
            proposal = web3.toBytes(hexstr=self.proposal_id)
        else:
            types = self.eip_712_type
            proposal = self.proposal_id

        payload = {
            "domain": self.domain,
            "message": {
                "from": self.safe.address,
                "space": space,
                "timestamp": int(time.time()),
                "proposal": proposal,
                "choice": json.dumps(choice_formatted, separators=(",", ":")),
                "reason": reason,
                "app": "snapshot",
                "metadata": json.dumps({}) if not metadata else metadata,
            },
            "primaryType": "Vote",
            "types": types,
        }

        validate_structured_data(payload)

        console.print("payload", payload)
        hash = self.create_payload_hash(payload)

        if is_weighted:
            for label, weight in choice_formatted.items():
                console.print(
                    f"signing vote for choice {label} with {weight * 100}% weight"
                )
        else:
            console.print(f"signing vote for choice {choice_formatted}")

        tx_data = self.sign_message_lib.signMessage.encode_input(hash)

        # NOTE: remove unused types as per endpoint 500 error
        payload["types"].pop("EIP712Domain")
        # NOTE: prior to json stringify, convert proposal[bytes -> string]
        payload["message"]["proposal"] = self.proposal_id

        # https://github.com/snapshot-labs/snapshot-relayer/blob/master/src/api.ts#L63
        r = requests.post(
            self.vote_relayer,
            headers=self.headers,
            data=json.dumps(
                {
                    "address": self.safe.address,
                    "data": payload,
                    "sig": "0x",
                },
                separators=(",", ":"),
            ),
        )

        # debugging their `msgHash`
        print(r.json()["id"])

        self.handle_response(r)

        safe_tx = self.safe.build_multisig_tx(
            to=registry.eth.gnosis.sign_message_lib, value=0, data=tx_data, operation=1
        )

        self.safe.post_safe_tx(safe_tx=safe_tx, skip_preview=True)
