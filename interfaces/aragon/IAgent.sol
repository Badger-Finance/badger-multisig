// SPDX-License-Identifier: MIT

pragma solidity >=0.5.0 <0.8.0;

interface IAgent {
    function transfer(address _token, address _to, uint256 _value) external;
}
