// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

interface IBadgerRegistry {
  function get(string calldata name) external view returns (address);

  function set(string memory key, address at) external;
}