// contracts/GasStation.sol
// SPDX-License-Identifier: MIT
pragma solidity 0.8.6;

import "@chainlink/contracts/src/v0.8/upkeeps/EthBalanceMonitor.sol";

/**
 * @title The GasStation Contract
 * @author gosuto.eth
 * @notice Custom implementation of Chainlink's EthBalanceMonitor; making sure
 * all of Badger's operational addresses always have enough ether.
 */
contract GasStation is EthBalanceMonitor {
    constructor(
        address keeperRegistryAddress, uint256 minWaitPeriodSeconds
    ) EthBalanceMonitor (
        keeperRegistryAddress, minWaitPeriodSeconds
    ) {}

    // TODO: rewrite to transfer exact amount needed to reach minBalanceWei??
    // /**
    // * @notice Send funds to the addresses provided
    // * @param needsFunding the list of addresses to fund (addresses must be pre-approved)
    // */
    // function topUp(address[] memory needsFunding) public whenNotPaused {
    //     uint256 minWaitPeriodSeconds = s_minWaitPeriodSeconds;
    //     Target memory target;
    //     for (uint256 idx = 0; idx < needsFunding.length; idx++) {
    //         target = s_targets[needsFunding[idx]];
    //         if (
    //             target.isActive &&
    //             target.lastTopUpTimestamp + minWaitPeriodSeconds <= block.timestamp &&
    //             needsFunding[idx].balance < target.minBalanceWei
    //         ) {
    //         bool success = payable(needsFunding[idx]).send(target.topUpAmountWei);
    //         if (success) {
    //             s_targets[needsFunding[idx]].lastTopUpTimestamp = uint56(block.timestamp);
    //             emit TopUpSucceeded(needsFunding[idx]);
    //         } else {
    //             emit TopUpFailed(needsFunding[idx]);
    //         }
    //         }
    //         if (gasleft() < MIN_GAS_FOR_TRANSFER) {
    //             return;
    //         }
    //     }
    // }
}
