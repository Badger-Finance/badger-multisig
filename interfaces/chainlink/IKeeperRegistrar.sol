// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

interface IKeeperRegistrar {
    error AmountMismatch();
    error FunctionNotPermitted();
    error HashMismatch();
    error InsufficientPayment();
    error InvalidAdminAddress();
    error InvalidDataLength();
    error LinkTransferFailed(address to);
    error OnlyAdminOrOwner();
    error OnlyLink();
    error RegistrationRequestFailed();
    error RequestNotFound();
    error SenderMismatch();
    event AutoApproveAllowedSenderSet(
        address indexed senderAddress,
        bool allowed
    );
    event ConfigChanged(
        uint8 autoApproveConfigType,
        uint32 autoApproveMaxAllowed,
        address keeperRegistry,
        uint96 minLINKJuels
    );
    event OwnershipTransferRequested(address indexed from, address indexed to);
    event OwnershipTransferred(address indexed from, address indexed to);
    event RegistrationApproved(
        bytes32 indexed hash,
        string displayName,
        uint256 indexed upkeepId
    );
    event RegistrationRejected(bytes32 indexed hash);
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

    function getAutoApproveAllowedSender(address senderAddress)
        external
        view
        returns (bool);

    function getPendingRequest(bytes32 hash)
        external
        view
        returns (address, uint96);

    function getRegistrationConfig()
        external
        view
        returns (
            uint8 autoApproveConfigType,
            uint32 autoApproveMaxAllowed,
            uint32 approvedCount,
            address keeperRegistry,
            uint256 minLINKJuels
        );

    function onTokenTransfer(
        address sender,
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
        uint8 source,
        address sender
    ) external;

    function setAutoApproveAllowedSender(address senderAddress, bool allowed)
        external;

    function setRegistrationConfig(
        uint8 autoApproveConfigType,
        uint16 autoApproveMaxAllowed,
        address keeperRegistry,
        uint96 minLINKJuels
    ) external;

    function transferOwnership(address to) external;

    function typeAndVersion() external view returns (string memory);
}
