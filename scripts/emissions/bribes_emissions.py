from decimal import Decimal

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main(
    total_bvecvx_emit=0,
    total_badger_emit=0,
    starting_time=0,
    ending_time=0,
    badger_share=0.275,
    ops_fee=0.05,
):
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    rewards_logger = safe.contract(registry.eth.rewardsLogger)

    pct_badger_to_bvecvx = 1 - (1 / Decimal(badger_share) * Decimal(ops_fee))

    bvecvx_to_emit_to_bvecvx = Decimal(total_bvecvx_emit)
    badger_to_emit_to_bvecvx = Decimal(total_badger_emit) * Decimal(
        pct_badger_to_bvecvx
    )
    badger_to_emit_to_lp = Decimal(total_badger_emit) - badger_to_emit_to_bvecvx

    # print amounts for ref - double check
    print(
        f"Mantissa amount emitted to bvecvx sett is {int(bvecvx_to_emit_to_bvecvx)} bvecvx\n"
    )
    print(
        f"Mantissa amount emitted to bvecvx sett is {int(badger_to_emit_to_bvecvx)} BADGER\n"
    )
    print(
        f"Mantissa amount emitted to bvecvx LP sett is {int(badger_to_emit_to_lp)} BADGER\n"
    )
    print(
        f"Total Mantissa badger emitted is {int(badger_to_emit_to_bvecvx) + int(badger_to_emit_to_lp)}"
    )

    if ending_time > starting_time:
        duration = int(ending_time) - int(starting_time)
    else:
        print("Ending time is prior to starting time, introduce good params!")
        return

    rewards_logger.setUnlockSchedule(
        registry.eth.sett_vaults.bveCVX,
        registry.eth.sett_vaults.bveCVX,
        int(bvecvx_to_emit_to_bvecvx),
        int(starting_time),
        int(ending_time),
        duration,
    )
    rewards_logger.setUnlockSchedule(
        registry.eth.sett_vaults.bveCVX,
        registry.eth.treasury_tokens.BADGER,
        int(badger_to_emit_to_bvecvx),
        int(starting_time),
        int(ending_time),
        duration,
    )
    rewards_logger.setUnlockSchedule(
        registry.eth.sett_vaults["bbveCVX-CVX-f"],
        registry.eth.treasury_tokens.BADGER,
        int(badger_to_emit_to_lp),
        int(starting_time),
        int(ending_time),
        duration,
    )

    safe.post_safe_tx()
