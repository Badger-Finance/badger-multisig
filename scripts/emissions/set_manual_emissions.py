from brownie import Wei

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


STARTING_TIME = 1664582400
DAYS = 7
DURATION = 60 * 60 * 24 * DAYS
ENDING_TIME = STARTING_TIME + DURATION


def main():
    safe = GreatApeSafe(r.badger_wallets.techops_multisig)
    safe.init_badger()
    rewards_logger = safe.contract(r.rewardsLogger)

    rewards_logger.setUnlockSchedule(
        r.sett_vaults.bcrvRenBTC,  # beneficiary,
        r.treasury_tokens.BADGER,  # payout token
        Wei(f"{476} ether"),
        STARTING_TIME,
        ENDING_TIME,
        DURATION,
    )
    rewards_logger.setUnlockSchedule(
        r.sett_vaults.bdxsBadgerWeth,  # beneficiary,
        r.treasury_tokens.BADGER,  # payout token
        Wei(f"{381} ether"),
        STARTING_TIME,
        ENDING_TIME,
        DURATION,
    )

    safe.post_safe_tx()
