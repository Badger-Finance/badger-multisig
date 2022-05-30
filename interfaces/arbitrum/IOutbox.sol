// SPDX-License-Identifier: MIT
pragma solidity >=0.5.0 <0.8.0;

interface IOutbox {
    event OutBoxTransactionExecuted(
        address indexed destAddr,
        address indexed l2Sender,
        uint256 indexed outboxEntryIndex,
        uint256 transactionIndex
    );
    event OutboxEntryCreated(
        uint256 indexed batchNum,
        uint256 outboxEntryIndex,
        bytes32 outputRoot,
        uint256 numInBatch
    );

    function OUTBOX_VERSION() external view returns (uint128);

    function bridge() external view returns (address);

    function calculateItemHash(
        address l2Sender,
        address destAddr,
        uint256 l2Block,
        uint256 l1Block,
        uint256 l2Timestamp,
        uint256 amount,
        bytes memory calldataForL1
    ) external pure returns (bytes32);

    function calculateMerkleRoot(
        bytes32[] memory proof,
        uint256 path,
        bytes32 item
    ) external pure returns (bytes32);

    function executeTransaction(
        uint256 batchNum,
        bytes32[] memory proof,
        uint256 index,
        address l2Sender,
        address destAddr,
        uint256 l2Block,
        uint256 l1Block,
        uint256 l2Timestamp,
        uint256 amount,
        bytes memory calldataForL1
    ) external;

    function initialize(address _rollup, address _bridge) external;

    function isMaster() external view returns (bool);

    function l2ToL1BatchNum() external view returns (uint256);

    function l2ToL1Block() external view returns (uint256);

    function l2ToL1EthBlock() external view returns (uint256);

    function l2ToL1OutputId() external view returns (bytes32);

    function l2ToL1Sender() external view returns (address);

    function l2ToL1Timestamp() external view returns (uint256);

    function outboxEntries(uint256) external view returns (bytes32 root);

    function outboxEntryExists(uint256 batchNum) external view returns (bool);

    function processOutgoingMessages(
        bytes memory sendsData,
        uint256[] memory sendLengths
    ) external;

    function rollup() external view returns (address);
} 