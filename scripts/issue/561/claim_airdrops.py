from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import interface, exceptions
from typing import List, Dict
from hexbytes import HexBytes
from eth_typing import HexStr
from web3 import Web3
import json
import os
from rich.console import Console


recipients = [
    r.badger_wallets.treasury_ops_multisig,    
    r.badger_wallets.treasury_vault_multisig,
    r.badger_wallets.treasury_voter_multisig,
    r.badger_wallets.ibbtc_multisig,
]


def main(msig_address):
    msig = GreatApeSafe(msig_address)
    aura_airdrop = interface.AuraMerkleDrop(r.aura.merkle_drop, owner=msig.account)

    # https://raw.githubusercontent.com/aurafinance/aura-token-allocation/master/artifacts/initial/allocations.csv
    with open('scripts/issue/561/airdrop_list.json', 'r') as f:
        airdrop_list = json.load(f)

    if not aura_airdrop.hasClaimed(msig_address):
        msig.take_snapshot(tokens=[r.treasury_tokens.AURA])

        with open(f'scripts/issue/561/proofs/{msig_address}.json', 'r') as f:
            proof = json.load(f)['account']

        amount = airdrop_list[msig.address]
        lock = False
        aura_airdrop.claim(proof, amount, lock)

        msig.print_snapshot()
        msig.post_safe_tx()
    else:
        print(f'Recipient: {msig_address} has already claimed')
