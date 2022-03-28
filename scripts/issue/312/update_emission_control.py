from brownie import interface, Contract

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

FINAL_TOKEN_WEIGHT = 5000

def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    emission_control = interface.IEmissionControl(registry.eth.EmissionControl, owner=safe.account)

    # Check inital token weight to ensure upgrade hasn't already happened
    initial_token_weight = emission_control.tokenWeight(registry.eth.sett_vaults.bcrvBadger)
    assert initial_token_weight != FINAL_TOKEN_WEIGHT, f"Already set to correct token weight: {initial_token_weight}"

    emission_control.setTokenWeight(registry.eth.sett_vaults.bcrvBadger, FINAL_TOKEN_WEIGHT)

    updated_token_weight = emission_control.tokenWeight(registry.eth.sett_vaults.bcrvBadger)
    assert updated_token_weight == FINAL_TOKEN_WEIGHT, f"Incorrect final token weight set: {updated_token_weight}"

    safe.post_safe_tx()
