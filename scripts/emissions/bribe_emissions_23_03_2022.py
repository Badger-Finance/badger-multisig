from brownie import Wei

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


# addresses involved in the schedules from emissions - politician msig
bvecvx_address = registry.eth.sett_vaults.bveCVX
ibbtc_address = registry.eth.sett_vaults.bcrvIbBTC
bvecvxlp_address = "0x937B8E917d0F36eDEBBA8E459C5FB16F3b315551" ## TODO handle .map and -'s in name
badger_address = registry.eth.treasury_tokens.BADGER


def main(total_bvecvx_emit=22435841532164025814838, total_badger_emit=23546200054934510237933, badger_pct_bvecvxlp=18.2, starting_time=1648166400, ending_time=1649376000):
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    rewards_logger = safe.contract(registry.eth.rewardsLogger)

    pct_formatted_badger_bvecvxlp = badger_pct_bvecvxlp / 100
    pct_formatted_badger_bvecvx = 1-pct_formatted_badger_bvecvxlp

    BVECVX_TO_EMIT_DURING_PERIOD_BVECVX = total_bvecvx_emit
    BADGER_TO_EMIT_DURING_PERIOD_BVECVX = total_badger_emit * pct_formatted_badger_bvecvx
    BADGER_TO_EMIT_DURING_PERIOD_LP = total_badger_emit - BADGER_TO_EMIT_DURING_PERIOD_BVECVX

    # print amounts for ref - double check
    print(
        f"Mantissa amount emitted to bvecvx sett is {BVECVX_TO_EMIT_DURING_PERIOD_BVECVX} bvecvx\n"
    )
    print(
        f"Mantissa amount emitted to bvecvx sett is {BADGER_TO_EMIT_DURING_PERIOD_BVECVX} BADGER\n"
    )
    print(
        f"Mantissa amount emitted to bvecvx LP sett is {BADGER_TO_EMIT_DURING_PERIOD_LP} BADGER\n"
    )
    print(
        f"Total Mantissa badger emitted is{BADGER_TO_EMIT_DURING_PERIOD_BVECVX + BADGER_TO_EMIT_DURING_PERIOD_LP}"
    )

    if ending_time > starting_time:
        DURATION = int(ending_time) - int(starting_time)
    else:
        print("Ending time is prior to starting time, introduce good params!")
        return

    rewards_logger.setUnlockSchedule(
        bvecvx_address,
        bvecvx_address,
        int(BVECVX_TO_EMIT_DURING_PERIOD_BVECVX),
        int(starting_time),
        int(ending_time),
        DURATION,
    )
    rewards_logger.setUnlockSchedule(
        badger_address,
        bvecvx_address,
        int(BADGER_TO_EMIT_DURING_PERIOD_BVECVX),
        int(starting_time),
        int(ending_time),
        DURATION,
    )

    rewards_logger.setUnlockSchedule(
        badger_address,
        bvecvxlp_address,
        int(BADGER_TO_EMIT_DURING_PERIOD_LP),
        int(starting_time),
        int(ending_time),
        DURATION,
    )

    safe.post_safe_tx()
