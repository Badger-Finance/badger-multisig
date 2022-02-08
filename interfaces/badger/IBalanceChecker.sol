// SPDX-License-Identifier: MIT
pragma solidity >=0.6.0;

// Generic address whitelist.
interface IBalanceChecker {
    // Checks if address exists in whitelist.
    function verifyBalance(address token, address account, uint256 amount) external returns (bool);
}
