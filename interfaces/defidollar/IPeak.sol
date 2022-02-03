// SPDX-License-Identifier: MIT

pragma solidity 0.6.11;

interface IPeak {
    function mint(
        uint256 poolId,
        uint256 inAmount,
        bytes32[] calldata merkleProof
    ) external returns (uint256);

    function approveContractAccess(address account) external;

    function approved(address) external view returns (bool);

    function redeem(uint256 poolId, uint256 inAmount) external returns (uint256);

    function portfolioValue() external view returns (uint256);

    function core() external view returns (address);

    function numPools() external view returns (uint256);

    function owner() external view returns (address);

    function byvWBTC() external view returns (address);

    function pools(uint256) external view returns (address);

    function guardian() external view returns (address);

    function setGuardian(address) external;

    function paused() external view returns (bool);
}