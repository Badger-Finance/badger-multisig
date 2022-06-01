// SPDX-License-Identifier: MIT
pragma solidity ^0.7.6;

interface IUpkeepRegistrationRequests {
    event ConfigChanged(
        bool enabled,
        uint32 windowSizeInBlocks,
        uint16 allowedPerWindow,
        address keeperRegistry,
        uint256 minLINKJuels
    );
    event OwnershipTransferRequested(address indexed from, address indexed to);
    event OwnershipTransferred(address indexed from, address indexed to);
    event RegistrationApproved(
        bytes32 indexed hash,
        string displayName,
        uint256 indexed upkeepId
    );
    event RegistrationRequested(
        bytes32 indexed hash,
        string name,
        bytes encryptedEmail,
        address indexed upkeepContract,
        uint32 gasLimit,
        address adminAddress,
        bytes checkData,
        uint96 amount,
        uint8 indexed source
    );

    function LINK() external view returns (address);

    function acceptOwnership() external;

    function approve(
        string memory name,
        address upkeepContract,
        uint32 gasLimit,
        address adminAddress,
        bytes memory checkData,
        bytes32 hash
    ) external;

    function cancel(bytes32 hash) external;

    function getPendingRequest(bytes32 hash)
        external
        view
        returns (address, uint96);

    function getRegistrationConfig()
        external
        view
        returns (
            bool enabled,
            uint32 windowSizeInBlocks,
            uint16 allowedPerWindow,
            address keeperRegistry,
            uint256 minLINKJuels,
            uint64 windowStart,
            uint16 approvedInCurrentWindow
        );

    function onTokenTransfer(
        address,
        uint256 amount,
        bytes memory data
    ) external;

    function owner() external view returns (address);

    function register(
        string memory name,
        bytes memory encryptedEmail,
        address upkeepContract,
        uint32 gasLimit,
        address adminAddress,
        bytes memory checkData,
        uint96 amount,
        uint8 source
    ) external;

    function setRegistrationConfig(
        bool enabled,
        uint32 windowSizeInBlocks,
        uint16 allowedPerWindow,
        address keeperRegistry,
        uint256 minLINKJuels
    ) external;

    function transferOwnership(address _to) external;
}
