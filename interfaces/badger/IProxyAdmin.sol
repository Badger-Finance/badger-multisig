// SPDX-License-Identifier: MIT
pragma solidity >=0.5.0 <0.8.0;

interface IProxyAdmin {
    function upgrade(address proxy, address implementation) external;

    function changeProxyAdmin(address proxy, address newAdmin) external;

    function owner() external view returns (address);
}
