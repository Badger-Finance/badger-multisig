from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console
from brownie import interface
from decimal import Decimal

import json

C = Console()

DEPRECATED_STRATS = {
    "native.bauraBal": "v1.2",
    "native.b80BADGER_20WBTC": "v1",
    "native.b40WBTC_40DIGG_20graviAURA": "v1",
}

EPOCH_IDS = ["epoch1", "epoch2"]


def main():
    safe = GreatApeSafe(r.badger_wallets.techops_multisig)
    aura = safe.contract(r.treasury_tokens.AURA)

    total_claim_amounts = {
        "native.bauraBal": 0,
        "native.b80BADGER_20WBTC": 0,
        "native.b40WBTC_40DIGG_20graviAURA": 0,
    }
    total_reward_amounts = {
        "native.bauraBal": 0,
        "native.b80BADGER_20WBTC": 0,
        "native.b40WBTC_40DIGG_20graviAURA": 0,
    }

    total_aura_claimed = 0

    for epoch in EPOCH_IDS:
        C.print(f"Claiming {epoch}")
        epoch_reward_amounts = {}
        epoch_claim_amounts = {}
        epoch_reward_total_amounts = 0
        epoch_claim_total_amounts = 0

        with open(f"scripts/issue/1086/{epoch}/rewards.json") as fp:
            epoch_rewards = json.load(fp)

        with open(f"scripts/issue/1086/{epoch}/claimsExact.json") as fp:
            claims_exact = json.load(fp)
            claim_exact_per_epoch = int(claims_exact["claims"][safe.address])

        for key, version in DEPRECATED_STRATS.items():
            try:
                epoch_reward_amounts[key] = int(
                    float(epoch_rewards[r.strategies._deprecated[key][version]]) * 1e18
                )
                total_reward_amounts[key] += epoch_reward_amounts[key]
                epoch_reward_total_amounts += epoch_reward_amounts[key]
            except:
                C.print(f"No rewards for {key} on {epoch}")

        ## Identify amount of AURA to transfer to each strat in proportion to its
        ## BAL rewards per epoch
        for key, _ in DEPRECATED_STRATS.items():
            try:
                epoch_claim_amounts[key] = (
                    Decimal(epoch_reward_amounts[key])
                    * Decimal(claim_exact_per_epoch)
                    / Decimal(epoch_reward_total_amounts)
                )
                total_claim_amounts[key] += epoch_claim_amounts[key]
                epoch_claim_total_amounts += epoch_claim_amounts[key]
            except:
                C.print(f"No AURA to claim for {key} on {epoch}")
        assert epoch_claim_total_amounts == claim_exact_per_epoch

        ## Claim AURA for current Epoch
        with open(f"scripts/issue/1086/{epoch}/proofs.json") as fp:
            proofs = json.load(fp)
            proof = proofs[safe.address]

        balance_before = aura.balanceOf(safe.address)
        aura_airdrop = interface.IAuraMerkleDropV2(
            r.aura[f"aura_merkle_drop_v2_{epoch}"], owner=safe.account
        )
        aura_airdrop.claim(proof, claim_exact_per_epoch, False, safe.address)
        assert claim_exact_per_epoch == aura.balanceOf(safe.address) - balance_before
        C.print(f"AURA claimed for {epoch}:", claim_exact_per_epoch)
        total_aura_claimed += claim_exact_per_epoch

    C.print("\nTotal Claim Amounts per Strat:", total_claim_amounts)
    C.print("\nTotal AURA claimed:", total_aura_claimed)

    # Distribute AURA in proportions to each strat
    total_aura_transferred = 0
    for key, amount in total_claim_amounts.items():
        strat_address = r.strategies[key]
        total_aura_transferred += amount
        C.print(f"Transfering {float(amount) / 1e18} to {key} at {strat_address}")
        balance_before = aura.balanceOf(strat_address)
        aura.transfer(strat_address, amount)
        assert int(amount) == aura.balanceOf(strat_address) - balance_before
    C.print("Total AURA transferred:", total_aura_claimed)
    assert total_aura_transferred == total_aura_claimed

    safe.post_safe_tx()
