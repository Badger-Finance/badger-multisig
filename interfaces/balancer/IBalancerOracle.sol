// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.0;

interface IBalancerOracle {
    error BalancerOracle__TWAPOracleNotReady();
    event OwnershipTransferred(address indexed user, address indexed newOwner);
    event SetParams(
        uint16 multiplier,
        uint56 secs,
        uint56 ago,
        uint128 minPrice
    );

    function ago() external view returns (uint56);

    function balancerTwapOracle() external view returns (address);

    function getPrice() external view returns (uint256 price);

    function minPrice() external view returns (uint128);

    function multiplier() external view returns (uint16);

    function owner() external view returns (address);

    function secs() external view returns (uint56);

    function setParams(
        uint16 multiplier_,
        uint56 secs_,
        uint56 ago_,
        uint128 minPrice_
    ) external;

    function transferOwnership(address newOwner) external;
}
