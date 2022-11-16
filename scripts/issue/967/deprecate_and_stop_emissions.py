from brownie import Wei, interface, chain
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from decimal import Decimal
import time

# addresses involved
BIBBTCCRV = registry.eth.sett_vaults.bcrvIbBTC
BRENCRV = registry.eth.sett_vaults.bcrvRenBTC
LINK = registry.eth.treasury_tokens.LINK
BADGER = registry.eth.treasury_tokens.BADGER

# Empty schedule parameters
START = 1668620976
END = 1668620976
DURATION = 0
AMOUNT = 0
INDEX = 39

# Dripper and keeper constants
UPKEEP_ID_TREE_22Q4 = 141  # https://automation.chain.link/mainnet/141

# Tree BADGER deficit
TREE_BADGER_DEFICIT = Wei(f"{33450.0339164155} ether")

# Tree bcvxCRV BADGER deficit
ORIGINAL_SCHEDULE_START = 1667606400
ORIGINAL_SCHEDULE_END = 1672531200
ORIGINAL_DURATION_WEEKS = Decimal(
    (ORIGINAL_SCHEDULE_END - ORIGINAL_SCHEDULE_START) / 604800
)
TOTAL_AMOUNT = 12637714285714284415007
AMOUNT_PER_WEEK = Wei(f"{1552} ether")


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    tree = GreatApeSafe(registry.eth.badger_wallets.badgertree)
    safe.init_badger()
    safe.init_chainlink()

    safe.take_snapshot([BADGER])
    trops.take_snapshot([BADGER])
    tree.take_snapshot([BADGER])

    # Deprecate vaults on registry
    safe.badger.demote_vault(BIBBTCCRV, 0)
    assert (
        safe.badger.registry_v2.productionVaultInfoByVault(BIBBTCCRV).dict()["status"]
        == 0
    )
    safe.badger.demote_vault(BRENCRV, 0)
    assert (
        safe.badger.registry_v2.productionVaultInfoByVault(BRENCRV).dict()["status"]
        == 0
    )

    # Stop emissions
    rewards_logger = safe.contract(registry.eth.rewardsLogger)
    rewards_logger.modifyUnlockSchedule(
        int(INDEX),
        BIBBTCCRV,
        BADGER,
        Wei(f"{AMOUNT} ether"),
        int(START),
        int(END),
        DURATION,
    )
    assert (
        len(rewards_logger.getAllUnlockSchedulesFor(BIBBTCCRV)) == INDEX + 1
    )  # Modifying the latest schedule
    assert rewards_logger.getAllUnlockSchedulesFor(BIBBTCCRV)[INDEX][5] == 0

    # Cancel dripper upkeep
    safe.chainlink.keeper_registry.cancelUpkeep(UPKEEP_ID_TREE_22Q4)

    # Claw back BADGER from dripper
    badger = safe.contract(BADGER)
    dripper = safe.contract(registry.eth.drippers.tree_2022_q4)
    safe_balance_before = badger.balanceOf(safe)
    dripper_balance_before = badger.balanceOf(dripper)

    remaining_weeks = Decimal(
        (ORIGINAL_SCHEDULE_END - dripper.lastTimestamp()) / 604800
    )
    bcvxCRV_badger_deficit = int(Decimal(AMOUNT_PER_WEEK * remaining_weeks))

    dripper.sweep(badger.address)
    assert badger.balanceOf(safe) == dripper_balance_before + safe_balance_before

    print("BCVXCRV EMISSIONS REMAINING WEEKS", remaining_weeks)
    print("BCVXCRV EMISSIONS WEEKLY AMOUNT", AMOUNT_PER_WEEK)
    print("BCVXCRV EMISSIONS RAMINING AMOUNT", bcvxCRV_badger_deficit)
    print("TREE EMISSIONS RAMINING AMOUNT", TREE_BADGER_DEFICIT)

    # Transfer total deficit to the Tree
    total_deficit = TREE_BADGER_DEFICIT + bcvxCRV_badger_deficit
    print("TOTAL DEFICIT AMOUNT", total_deficit)
    badger.transfer(safe.badger.tree, total_deficit)

    # Transfer remaining to Trops
    remaining = badger.balanceOf(safe)
    badger.transfer(trops, remaining)

    trops.print_snapshot()
    tree.print_snapshot()
    safe.post_safe_tx()


def withdraw_link(simulation="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    safe.take_snapshot([LINK])
    link = safe.contract(LINK, interface.ILinkToken)

    if simulation == "true":
        safe.init_chainlink()
        safe.chainlink.keeper_registry.cancelUpkeep(UPKEEP_ID_TREE_22Q4)
        chain.sleep(3600)
        chain.mine(50)

    balance_before = link.balanceOf(safe)
    safe.chainlink.keeper_registry.withdrawFunds(UPKEEP_ID_TREE_22Q4, safe)
    assert balance_before < link.balanceOf(safe)

    safe.post_safe_tx()
