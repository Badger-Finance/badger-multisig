from decimal import Decimal
from brownie import Wei

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main(
    total_bvecvx_emit=22435841532164025814838,
    total_badger_emit=23546200054934510237933,
    starting_time=1648166400,
    ending_time=1649376000,
):
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    rewards_logger = safe.contract(registry.eth.rewardsLogger)

    # badger allocation: https://docs.google.com/spreadsheets/d/1R3dBig3f13jNgjTuNhLXcGVle1gxERNNKJD-2TAWgbE/edit#gid=612678328&range=B61
    pct_formatted_badger_bvecvxlp = (100 / 27.5) * 0.05
    pct_formatted_badger_bvecvx = 1 - pct_formatted_badger_bvecvxlp

    BVECVX_TO_EMIT_DURING_PERIOD_BVECVX = total_bvecvx_emit
    BADGER_TO_EMIT_DURING_PERIOD_BVECVX = Decimal(
        total_badger_emit * pct_formatted_badger_bvecvx
    )
    BADGER_TO_EMIT_DURING_PERIOD_LP = Decimal(
        total_badger_emit - BADGER_TO_EMIT_DURING_PERIOD_BVECVX
    )

    # print amounts for ref - double check
    print(
        f"Amount emitted to bvecvx sett is {Wei(BVECVX_TO_EMIT_DURING_PERIOD_BVECVX).to('ether')} bvecvx\n"
    )
    print(
        f"Amount emitted to bvecvx sett is {Wei(BADGER_TO_EMIT_DURING_PERIOD_BVECVX).to('ether')} BADGER\n"
    )
    print(
        f"Amount emitted to bvecvx LP sett is {Wei(BADGER_TO_EMIT_DURING_PERIOD_LP).to('ether')} BADGER\n"
    )
    print(
        f"Total badger emitted is {Wei(BADGER_TO_EMIT_DURING_PERIOD_BVECVX + BADGER_TO_EMIT_DURING_PERIOD_LP).to('ether')}\n"
    )

    if ending_time > starting_time:
        DURATION = int(ending_time) - int(starting_time)
    else:
        print("Ending time is prior to starting time, introduce good params!")
        return

    rewards_logger.setUnlockSchedule(
        registry.eth.sett_vaults.bveCVX,
        registry.eth.sett_vaults.bveCVX,
        int(BVECVX_TO_EMIT_DURING_PERIOD_BVECVX),
        int(starting_time),
        int(ending_time),
        DURATION,
    )
    rewards_logger.setUnlockSchedule(
        registry.eth.sett_vaults.bveCVX,
        registry.eth.treasury_tokens.BADGER,
        int(BADGER_TO_EMIT_DURING_PERIOD_BVECVX),
        int(starting_time),
        int(ending_time),
        DURATION,
    )

    rewards_logger.setUnlockSchedule(
        registry.eth.sett_vaults["bbveCVX-CVX-f"],
        registry.eth.treasury_tokens.BADGER,
        int(BADGER_TO_EMIT_DURING_PERIOD_LP),
        int(starting_time),
        int(ending_time),
        DURATION,
    )

    safe.post_safe_tx()
