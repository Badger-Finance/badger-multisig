// SPDX-License-Identifier: MIT
pragma solidity ^0.5.0;

interface IAdminUpgradeabilityProxy {
    event AdminChanged(address previousAdmin, address newAdmin);
    event Upgraded(address indexed implementation);
    function() external payable;

    function admin() external returns (address);

    function changeAdmin(address newAdmin) external;

    function implementation() external returns (address);

    function upgradeTo(address newImplementation) external;

    function upgradeToAndCall(address newImplementation, bytes calldata data)
        external
        payable;
}
