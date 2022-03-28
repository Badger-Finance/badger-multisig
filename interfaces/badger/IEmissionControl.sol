// SPDX-License-Identifier: MIT
pragma solidity >=0.6.0;

interface IEmissionControl {

    function tokenWeight(address _address) external returns (uint256);

    function setTokenWeight(address _token, uint256 _weight) external;
    
}
