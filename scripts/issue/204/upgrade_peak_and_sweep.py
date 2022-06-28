from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface
import brownie

SAFE = GreatApeSafe(registry.eth.badger_wallets.dfdBadgerShared)

NEW_LOGIC = registry.eth.logic["BadgerSettPeak"]
PEAK = interface.IPeak(registry.eth.peaks.badgerPeak, owner=SAFE.account)
BVECVX = interface.ERC20(registry.eth.treasury_tokens.bveCVX)
BVECVX_VOTING_MULTI = registry.eth.badger_wallets.treasury_voter_multisig
BALANCE_CHECKER = interface.IBalanceChecker(registry.eth.helpers.balance_checker, owner=SAFE.account)

# Atomically upgrades the BadgerSettPeak contract and calls the sweeping function
# to recover the bveCVX stuck into the treasury vault

def main():

    # Get all storage variables, we'll use them later
    portfolioValue = PEAK.portfolioValue()
    core = PEAK.core()
    numPools = PEAK.numPools()
    owner = PEAK.owner()
    pools = PEAK.pools(0) # Currently only one pool

    # Upgrade logic
    PEAK_PROXY = interface.IUpgradableProxy(
        registry.eth.peaks.badgerPeak,
        owner=SAFE.account
    )
    assert PEAK_PROXY.owner() == SAFE.account
    PEAK_PROXY.updateImplementation(NEW_LOGIC)

    # Checking all variables are as expected
    assert portfolioValue == PEAK.portfolioValue()
    assert core == PEAK.core()
    assert numPools == PEAK.numPools()
    assert owner == PEAK.owner()
    assert pools == PEAK.pools(0)

    # Sweeps stuck bveCVX
    vault_balance_before = BVECVX.balanceOf(BVECVX_VOTING_MULTI)
    peak_balance_before = BVECVX.balanceOf(PEAK.address)

    PEAK.sweepUnprotectedToken(BVECVX.address, BVECVX_VOTING_MULTI)

    BALANCE_CHECKER.verifyBalance(
        BVECVX.address,
        BVECVX_VOTING_MULTI,
        vault_balance_before + peak_balance_before
    )
    assert BVECVX.balanceOf(PEAK.address) == 0


    SAFE.post_safe_tx()
