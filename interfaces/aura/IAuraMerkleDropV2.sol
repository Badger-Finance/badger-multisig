// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

interface IAuraMerkleDropV2 {
    event Claimed(address addr, uint256 amt, bool locked);
    event DaoSet(address newDao);
    event ExpiredWithdrawn(uint256 amount);
    event Initialized();
    event LockerSet(address newLocker);
    event Rescued();
    event RootSet(bytes32 newRoot);
    event StartedEarly();

    function aura() external view returns (address);

    function auraLocker() external view returns (address);

    function claim(
        bytes32[] memory _proof,
        uint256 _amount,
        bool _lock,
        address addr
    ) external returns (bool);

    function dao() external view returns (address);

    function deployTime() external view returns (uint256);

    function expiryTime() external view returns (uint256);

    function hasClaimed(address) external view returns (bool);

    function merkleRoot() external view returns (bytes32);

    function rescueReward() external;

    function setDao(address _newDao) external;

    function setLocker(address _newLocker) external;

    function setRoot(bytes32 _merkleRoot) external;

    function startEarly() external;

    function startTime() external view returns (uint256);

    function withdrawExpired() external;
}