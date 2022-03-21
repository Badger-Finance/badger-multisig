from brownie import Wei

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

# addresses involved most likely moving forward to Q2, leaving as default
ibbtc_sett = registry.eth.sett_vaults.bcrvIbBTC
badger_address = registry.eth.treasury_tokens.BADGER


def main(
    index=0,
    starting_time=0,
    ending_time=0,
    amount_emitted=0,
    beneficiary_addr=ibbtc_sett,
    token_emitted=badger_address,
):
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    rewards_logger = safe.contract(registry.eth.rewardsLogger)

    if ending_time > starting_time:
        duration = int(ending_time) - int(starting_time)
    else:
        print("Ending time is prior to starting time, introduce good params!")
        return

    rewards_logger.modifyUnlockSchedule(
        int(index),
        beneficiary_addr,
        token_emitted,
        Wei(f"{amount_emitted} ether"),
        int(starting_time),
        int(ending_time),
        duration,
    )

    safe.post_safe_tx()
