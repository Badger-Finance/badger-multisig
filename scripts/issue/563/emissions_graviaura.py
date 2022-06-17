from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main(amount=25000000000000000000000, start_ts=1655481600, end_ts=1658505600):
    techops = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)

    rewards_logger = techops.contract(registry.eth.rewardsLogger)

    duration = int(end_ts) - int(start_ts)

    rewards_logger.setUnlockSchedule(
        registry.eth.sett_vaults.graviAURA,
        registry.eth.treasury_tokens.BADGER,
        int(amount),
        int(start_ts),
        int(end_ts),
        duration,
    )

    techops.post_safe_tx()
