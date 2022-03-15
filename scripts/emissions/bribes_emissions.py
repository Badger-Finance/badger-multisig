from brownie import Wei

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


# addresses involved in the schedules from emissions - politician msig
bvecvx_address = registry.eth.sett_vaults.bveCVX
ibbtc_address = registry.eth.sett_vaults.bcrvIbBTC


def main(total_to_emit=0, pct_bvecvx=0, pct_ibbtc=0, starting_time=0, ending_time=0):
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    rewards_logger = safe.contract(registry.eth.rewardsLogger)

    pct_formatted_bvecvx = float(pct_bvecvx) / 100
    pct_formatted_ibbtc = float(pct_ibbtc) / 100

    AMOUNT_TO_EMIT_DURING_PERIOD_BVECVX = float(
        float(total_to_emit) * pct_formatted_bvecvx
    )
    AMOUNT_TO_EMIT_DURING_PERIOD_IBBTC = float(
        float(total_to_emit) * pct_formatted_ibbtc
    )

    # print amounts for ref - double check
    print(
        f"Amount emitted to bvecvx sett is {AMOUNT_TO_EMIT_DURING_PERIOD_BVECVX} bvecvx\n"
    )
    print(
        f"Amount emitted to ibbtc sett is {AMOUNT_TO_EMIT_DURING_PERIOD_IBBTC} bvecvx\n"
    )

    if ending_time > starting_time:
        DURATION = int(ending_time) - int(starting_time)
    else:
        print("Ending time is prior to starting time, introduce good params!")
        return

    rewards_logger.setUnlockSchedule(
        bvecvx_address,
        bvecvx_address,
        Wei(f"{AMOUNT_TO_EMIT_DURING_PERIOD_BVECVX} ether"),
        int(starting_time),
        int(ending_time),
        DURATION,
    )

    rewards_logger.setUnlockSchedule(
        ibbtc_address,
        bvecvx_address,
        Wei(f"{AMOUNT_TO_EMIT_DURING_PERIOD_IBBTC} ether"),
        int(starting_time),
        int(ending_time),
        DURATION,
    )

    safe.post_safe_tx()
