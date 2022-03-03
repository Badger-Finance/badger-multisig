// SPDX-License-Identifier: MIT
pragma solidity >=0.5.0 <0.8.0;

interface ISimpleTimelockWithVoting {
    function beneficiary() external view returns (address);

    function token() external view returns (address);

    function releaseTime() external view returns (uint256);

    function setBeneficiary(address beneficiary) external returns (address);
    
    function release() external;
}
