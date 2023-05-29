// SPDX-License-Identifier: MIT
pragma solidity ^0.4.15;

interface IMultisigWalletWithDailyLimit {
    function owners(uint256) external view returns (address);

    function removeOwner(address owner) external;

    function revokeConfirmation(uint256 transactionId) external;

    function isOwner(address) external view returns (bool);

    function confirmations(uint256, address) external view returns (bool);

    function calcMaxWithdraw() external view returns (uint256);

    function getTransactionCount(
        bool pending,
        bool executed
    ) external view returns (uint256 count);

    function dailyLimit() external view returns (uint256);

    function lastDay() external view returns (uint256);

    function addOwner(address owner) external;

    function isConfirmed(uint256 transactionId) external view returns (bool);

    function getConfirmationCount(
        uint256 transactionId
    ) external view returns (uint256 count);

    function transactions(
        uint256
    )
        external
        view
        returns (
            address destination,
            uint256 value,
            bytes memory data,
            bool executed
        );

    function getOwners() external view returns (address[] memory);

    function getTransactionIds(
        uint256 from,
        uint256 to,
        bool pending,
        bool executed
    ) external view returns (uint256[] memory _transactionIds);

    function getConfirmations(
        uint256 transactionId
    ) external view returns (address[] memory _confirmations);

    function transactionCount() external view returns (uint256);

    function changeRequirement(uint256 _required) external;

    function confirmTransaction(uint256 transactionId) external;

    function submitTransaction(
        address destination,
        uint256 value,
        bytes data
    ) external returns (uint256 transactionId);

    function changeDailyLimit(uint256 _dailyLimit) external;

    function MAX_OWNER_COUNT() external view returns (uint256);

    function required() external view returns (uint256);

    function replaceOwner(address owner, address newOwner) external;

    function executeTransaction(uint256 transactionId) external;

    function spentToday() external view returns (uint256);

    // fallback() external payable;

    event DailyLimitChange(uint256 dailyLimit);
    event Confirmation(address indexed sender, uint256 indexed transactionId);
    event Revocation(address indexed sender, uint256 indexed transactionId);
    event Submission(uint256 indexed transactionId);
    event Execution(uint256 indexed transactionId);
    event ExecutionFailure(uint256 indexed transactionId);
    event Deposit(address indexed sender, uint256 value);
    event OwnerAddition(address indexed owner);
    event OwnerRemoval(address indexed owner);
    event RequirementChange(uint256 required);
}
