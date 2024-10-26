import time

"""
Reverting means a mismatch on the hash production and relayers may be looking for a different
hash from the safe events and the vote may not show up ever in the snapshot space as result
"""


def test_hash_single_choice(snapshot_single_choice):
    ts = time.time()
    singe_choice = "yes"
    hash_class_generated, payload = snapshot_single_choice.create_payload_hash(
        timestamp=ts, choice=singe_choice
    )

    # debugging eip712 hash produce from https://pypi.org/project/eip712/ package
    print("Class generated hash:", hash_class_generated.hex())

    # NOTE: remove unused types as per endpoint 500 error
    payload["types"].pop("EIP712Domain")
    # NOTE: prior to json stringify, convert proposal[bytes -> string]
    payload["message"]["proposal"] = snapshot_single_choice.proposal_id
    hash_api_generated = snapshot_single_choice.post_payload_relayer_api(payload)

    # debugging api `msgHash`
    print("API generated hash:", hash_api_generated)

    assert hash_class_generated.hex() == hash_api_generated


def test_hash_multi_choice(snapshot_multi_choice):
    ts = time.time()
    multi_choice = {"80/20 BADGER/WBTC": 1, "40/40/20 WBTC/DIGG/graviAURA": 1}

    hash_class_generated, payload = snapshot_multi_choice.create_payload_hash(
        timestamp=ts, choice=multi_choice
    )

    # debugging eip712 hash produce from https://pypi.org/project/eip712/ package
    print("Class generated hash:", hash_class_generated.hex())

    # NOTE: remove unused types as per endpoint 500 error
    payload["types"].pop("EIP712Domain")
    # NOTE: prior to json stringify, convert proposal[bytes -> string]
    payload["message"]["proposal"] = snapshot_multi_choice.proposal_id
    hash_api_generated = snapshot_multi_choice.post_payload_relayer_api(payload)

    # debugging api `msgHash`
    print("API generated hash:", hash_api_generated)

    assert hash_class_generated.hex() == hash_api_generated
