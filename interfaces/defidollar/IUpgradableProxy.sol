// SPDX-License-Identifier: MIT

pragma solidity >=0.7.0 <0.9.0;

interface IUpgradableProxy {
    event OwnershipTransferred(
        address indexed previousOwner,
        address indexed newOwner
    );
    event ProxyUpdated(address indexed previousImpl, address indexed newImpl);

    fallback() external;

    function implementation() external view returns (address _impl);

    function owner() external view returns (address _owner);

    function proxyType() external pure returns (uint256 proxyTypeId);

    function transferOwnership(address newOwner) external;

    function updateImplementation(address _newProxyTo) external;
}