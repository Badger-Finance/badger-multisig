from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import Contract, interface

"""
  Lock Half of CVX in bveCVX via
"""

# Assert approximate integer
def approx(actual, expected, percentage_threshold):
    print(actual, expected, percentage_threshold)
    diff = int(abs(actual - expected))
    # 0 diff should automtically be a match
    if diff == 0:
        return True
    return diff < (actual * percentage_threshold // 100)


def main():

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_badger()
    safe.init_convex()

    ## Check both "rebalacing variables" are false to avoid messing up the math
    assert safe.badger.strat_bvecvx.processLocksOnRebalance() == False
    assert safe.badger.strat_bvecvx.harvestOnRebalance() == False

    ## Total Available
    """
      From https://etherscan.io/address/0x86ca553d5ae7cd0005552d6e275786d5043800bd#code#F1#L639

    """

    MAX_BPS = safe.badger.strat_bvecvx.MAX_BPS()

    locker = Contract.from_explorer(safe.badger.strat_bvecvx.LOCKER())

    balanceOfWant = safe.badger.strat_bvecvx.balanceOfWant()
    balanceInLock = locker.balanceOf(safe.badger.strat_bvecvx)
    totalCVXBalance = balanceOfWant + balanceInLock

    

    ## We want to lock half of what's in the Strategy
    


    ## Our Target is 50% of the CVX in the strat
    target_amount = balanceOfWant // 2

    ## in BPS
    as_bps = (target_amount + balanceInLock) * MAX_BPS // totalCVXBalance 

    print("as_bps")
    print(as_bps)

    ## Verify math makes sense
    newLockAmount = totalCVXBalance * as_bps // MAX_BPS

    print("newLockAmount")
    print(newLockAmount)

    cvxToLock = newLockAmount - balanceInLock

    print("cvxToLock")
    print(cvxToLock)

    assert approx(cvxToLock, target_amount, 1)

    ## Calculate what half of the strategy is as %, then lock that

    ## Goes to Vault
    expected_in_vault = balanceOfWant - cvxToLock

    # before_lock_balance = TODO


    before_balance_in_vault = safe.convex.cvx.balanceOf(registry.eth.sett_vaults.bveCVX)
    before_balance_of_locker = safe.convex.cvx.balanceOf(safe.badger.strat_bvecvx.LOCKER())

    
    ## Lock
    safe.badger.strat_bvecvx.manualRebalance(as_bps)

    after_balance_in_vault = safe.convex.cvx.balanceOf(registry.eth.sett_vaults.bveCVX)
    after_balance_of_locker = safe.convex.cvx.balanceOf(safe.badger.strat_bvecvx.LOCKER())

    assert approx(after_balance_in_vault - before_balance_in_vault, expected_in_vault, 1)
    assert approx(after_balance_of_locker - before_balance_of_locker, cvxToLock, 1)
    
    safe.post_safe_tx()