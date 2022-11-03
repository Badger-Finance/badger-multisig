from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import interface
import json


"""
eligble:
treasury voter: 0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b
ibbtc msig: 0xB76782B51BFf9C27bA69C77027e20Abd92Bcf3a8
ibbtc peak (todo: redirect): 0x41671BA1abcbA387b9b2B752c205e22e916BE6e3
trops: 0x042B32Ac6b453485e357938bdC38e0340d4b9276
vault: 0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e
"""


def main(msig_address):
    msig = GreatApeSafe(msig_address)

    aura_airdrop = interface.IAuraMerkleDrop(r.aura.merkle_drop, owner=msig.account)
    aura = msig.contract(r.treasury_tokens.AURA)

    # https://raw.githubusercontent.com/aurafinance/aura-token-allocation/master/artifacts/initial/allocations.csv
    with open("scripts/issue/561/airdrop_list.json", "r") as f:
        airdrop_list = json.load(f)

    if not aura_airdrop.hasClaimed(msig_address):
        msig.take_snapshot(tokens=[aura])

        with open(f"scripts/issue/561/proofs/{msig_address}.json", "r") as f:
            proof = json.load(f)["account"]

        is_voter = msig_address == r.badger_wallets.treasury_voter_multisig

        amount = airdrop_list[msig.address]
        lock = is_voter
        aura_airdrop.claim(proof, amount, lock)

        msig.print_snapshot()

        if not is_voter:
            aura.transfer(
                r.badger_wallets.treasury_voter_multisig, aura.balanceOf(msig)
            )

        msig.print_snapshot()
        msig.post_safe_tx()
    else:
        print(f"Recipient: {msig_address} has already claimed")
