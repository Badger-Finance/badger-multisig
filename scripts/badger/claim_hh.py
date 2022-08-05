import requests

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main(destination="0x042B32Ac6b453485e357938bdC38e0340d4b9276"): # trops
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)

    rewards = voter.contract(r.hidden_hand.rewards_distributor)

    hh_url = f"https://hhand.xyz/reward/1/{voter.address}"
    response = requests.get(hh_url)
    data = response.json()["data"]


    aggregate = {"tokens": [], "amounts": []}
    for item in data:
        aggregate["tokens"].append(item["token"])
        aggregate["amounts"].append(item["claimMetadata"]["amount"])
    
    voter.take_snapshot(tokens=aggregate["tokens"])

    rewards.claim(
        [
                (
                    item["claimMetadata"]["identifier"],
                    item["claimMetadata"]["account"],
                    item["claimMetadata"]["amount"],
                    item["claimMetadata"]["merkleProof"],
                )
                for item in data
            ]
    )

    print(dict(zip(aggregate["tokens"], aggregate["amounts"])))

    voter.print_snapshot()
