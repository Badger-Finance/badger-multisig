from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    techops = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    rewards_logger = techops.contract(registry.eth.rewardsLogger)

    schedules = rewards_logger.getUnlockSchedulesFor(
        registry.eth.sett_vaults.bslpWbtcDigg, registry.eth.treasury_tokens.DIGG
    )

    rewards_logger.modifyUnlockSchedule(
        int(len(schedules) - 1),
        registry.eth.sett_vaults.bslpWbtcDigg,
        registry.eth.treasury_tokens.DIGG,
        0,  # amount
        0,  # start_time
        0,  # ending_time
        0,  # duration
    )

    techops.post_safe_tx()
