from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import Contract, chain

# Emissions constants
EMISSION_AMOUNT = 37591575106071500000000  # 37591.5751060715
EMISSION_START = 1704067200  # 2024-01-01 00:00:00 UTC
EMISSION_END = 1706918400  # 2024-02-03 00:00:00 UTC
DURATION = EMISSION_END - EMISSION_START  # 2851200 (33 days)

# rembadger constants
OUTSTANDING_BADGER_DEPOSIT = 20703934702652000000000  # 20,703.934702652
OUTSTANDING_BADGER_DEPOSIT_PER_WEEK = OUTSTANDING_BADGER_DEPOSIT / 5  # 4140.7869405304


def rembadger_techops_operations(test=False):
    """
    The following operations are to be executed by the techops multisig:
    - Sweep BADGER from both drippers
    - Transfer BADGER to the treasury ops
    - Cancel upkeeps on both drippers
    - Post final emission schedule for remBADGER
    """
    safe = GreatApeSafe(r.badger_wallets.techops_multisig)
    safe.init_badger()

    # Contracts involved
    rembadger_2023 = safe.contract(r.drippers.rembadger_2023)
    tree_2023 = safe.contract(r.drippers.tree_2023)
    badger = safe.contract(r.treasury_tokens.BADGER)
    rembadger = safe.contract(r.sett_vaults.remBADGER)
    upkeep_manager = safe.contract(r.badger_wallets.upkeep_manager)
    rewards_logger = Contract.from_explorer(r.rewardsLogger, owner=safe.account)

    # Sweep BADGER from both drippers
    prev_balance = badger.balanceOf(safe.account)
    prev_rembadger_dripper_balance = badger.balanceOf(rembadger_2023.address)
    prev_tree_dripper_balance = badger.balanceOf(tree_2023.address)

    rembadger_2023.sweep(badger.address)
    tree_2023.sweep(badger.address)

    assert (
        badger.balanceOf(safe.account)
        == prev_balance + prev_rembadger_dripper_balance + prev_tree_dripper_balance
    )

    # Transfer BADGER to the treasury ops
    badger.transfer(
        r.badger_wallets.treasury_ops_multisig, badger.balanceOf(safe.account)
    )

    # Cancel upkeeps on both drippers
    upkeep_manager.cancelMemberUpkeep(rembadger_2023.address)
    upkeep_manager.cancelMemberUpkeep(tree_2023.address)

    # Post final emission schedule for remBADGER
    rewards_logger.setUnlockSchedule(
        rembadger.address,
        badger.address,
        EMISSION_AMOUNT,
        EMISSION_START,
        EMISSION_END,
        DURATION,
    )

    if not test:
        safe.post_safe_tx()


def clawback_link(test=False):
    """
    50 blocks after the two upkeeps are cancelled on the UpKeep Manager, their LINK can be clawed back and
    the memebers can be fully deleted from the contract's storage. To be called by TechOps.
    """
    safe = GreatApeSafe(r.badger_wallets.techops_multisig)
    upkeep_manager = safe.contract(r.badger_wallets.upkeep_manager)
    rembadger_2023 = safe.contract(r.drippers.rembadger_2023)
    tree_2023 = safe.contract(r.drippers.tree_2023)
    link = safe.contract(r.treasury_tokens.LINK)

    prev_balance = link.balanceOf(upkeep_manager.address)

    upkeep_manager.withdrawLinkFundsAndRemoveMember(rembadger_2023.address)
    upkeep_manager.withdrawLinkFundsAndRemoveMember(tree_2023.address)

    assert link.balanceOf(upkeep_manager.address) > prev_balance

    if not test:
        safe.post_safe_tx()


def test_techops_operations():
    rembadger_techops_operations(test=True)
    chain.mine(51)
    clawback_link(test=True)


def tree_top_up():
    """
    The following operation is to be executed by the treasury ops multisig once.
    """
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)

    # Contracts involved
    badger_tree = safe.contract(r.badger_wallets.badgertree)
    badger = safe.contract(r.treasury_tokens.BADGER)

    # Top up the tree
    prev_balance = badger.balanceOf(badger_tree.address)
    badger.transfer(badger_tree.address, EMISSION_AMOUNT)
    assert badger.balanceOf(badger_tree.address) == prev_balance + EMISSION_AMOUNT

    safe.post_safe_tx()


def rembadger_top_up():
    """
    The following operation is to be executed by the treasury ops multisig once a week until the end of the
    remBADGER program on 2024-02-03 00:00:00 UTC (5 times).
    """
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)

    # Contracts involved
    rembadger = safe.contract(r.sett_vaults.remBADGER)
    badger = safe.contract(r.treasury_tokens.BADGER)

    # Top up rembadger
    prev_balance = badger.balanceOf(rembadger.address)
    badger.transfer(rembadger.address, OUTSTANDING_BADGER_DEPOSIT_PER_WEEK)
    assert badger.balanceOf(rembadger.address) == prev_balance + (
        OUTSTANDING_BADGER_DEPOSIT_PER_WEEK
    )

    safe.post_safe_tx()
