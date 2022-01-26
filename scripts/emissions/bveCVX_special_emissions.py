from brownie import Wei

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


# UPDATE THESE VARIABLES WITH THE NEEDS FOR A NEW GUARD LAUNCH OR SIMILAR SCENARIO
STARTING_TIME = 1643241600
ENDING_TIME = 1644537600
AMOUNT_TO_EMIT_DURING_PERIOD = 100
DURATION = ENDING_TIME - STARTING_TIME


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    safe.init_badger()
    rewards_logger = safe.contract(registry.eth.rewardsLogger)

    rewards_logger.setUnlockSchedule(
        registry.eth.treasury_tokens.bveCVX,#beneficiary,
        registry.eth.treasury_tokens.bveCVX, #payout token
        Wei(f"{AMOUNT_TO_EMIT_DURING_PERIOD} ether"),
        STARTING_TIME,
        ENDING_TIME,
        DURATION,
    )

    safe.post_safe_tx()
