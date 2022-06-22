// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

interface IHarvestForwarder {
    event TreeDistribution(
        address indexed token, 
        uint256 amount, 
        uint indexed block_number,
        uint256 block_timestamp,
        address beneficiary
    );

    function distribute(address, uint256, address) external;

}
