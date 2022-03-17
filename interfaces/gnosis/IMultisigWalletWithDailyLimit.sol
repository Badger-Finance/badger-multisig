// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;

interface IMultisigWalletWithDailyLimit {
    function getOwners() external view returns (address[] memory);

    function addOwner(address owner) external;

    function removeOwner(address owner) external;

    function replaceOwner(address owner, address newOwner) external;

    function submitTransaction(
        address destination,
        uint256 value,
        bytes memory data
    ) external returns (uint256 transactionId);

    function confirmTransaction(uint256 transactionId) external;

    function getConfirmations(uint256 transactionId)
        external
        view
        returns (address[] memory _confirmations);

    function transactions(uint256 transactionId)
        external
        view
        returns (
            address,
            uint256,
            bytes memory,
            bool
        );
}