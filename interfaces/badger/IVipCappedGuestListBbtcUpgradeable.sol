// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

interface IVipCappedGuestListBbtcUpgradeable {
    event OwnershipTransferred(
        address indexed previousOwner,
        address indexed newOwner
    );
    event ProveInvitation(address indexed account, bytes32 indexed guestRoot);
    event SetGeyser(address geyser);
    event SetGuestRoot(bytes32 indexed guestRoot);
    event SetTotalDepositCap(uint256 cap);
    event SetUserDepositCap(uint256 cap);

    function authorized(
        address _guest,
        uint256 _amount,
        bytes32[] calldata _merkleProof
    ) external view returns (bool);

    function geyser() external view returns (address);

    function guestRoot() external view returns (bytes32);

    function guests(address) external view returns (bool);

    function initialize(address wrapper_) external;

    function owner() external view returns (address);

    function proveInvitation(address account, bytes32[] calldata merkleProof)
        external;

    function remainingTotalDepositAllowed() external view returns (uint256);

    function remainingUserDepositAllowed(address user)
        external
        view
        returns (uint256);

    function renounceOwnership() external;

    function setGuestRoot(bytes32 guestRoot_) external;

    function setGuests(address[] calldata _guests, bool[] calldata _invited)
        external;

    function setTotalDepositCap(uint256 cap_) external;

    function setUserDepositCap(uint256 cap_) external;

    function setWrapper(address wrapper_) external;

    function totalDepositCap() external view returns (uint256);

    function transferOwnership(address newOwner) external;

    function userDepositCap() external view returns (uint256);

    function wrapper() external view returns (address);
}