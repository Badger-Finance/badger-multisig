from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    techops = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)

    rewards_logger = techops.contract(registry.eth.rewardsLogger)

    rewards_logger.setUnlockSchedule(
        registry.eth.sett_vaults.graviAURA,
        registry.eth.treasury_tokens.BADGER,
        25000000000000000000000,  # 25k badger
        1655481600,  #  Friday, 17 June 2022 16:00:00 UTC
        1658505600,  # Friday, 22 July 2022 16:00:00 UTC
        3024000,
    )

    techops.post_safe_tx()
