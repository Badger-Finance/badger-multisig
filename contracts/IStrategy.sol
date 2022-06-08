// SPDX-License-Identifier: MIT
pragma solidity ^0.8.6;

interface IStrategy {
    function withdrawAll() external returns (uint256);
}
