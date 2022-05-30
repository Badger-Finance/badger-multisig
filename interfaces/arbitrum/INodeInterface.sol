// SPDX-License-Identifier: MIT
pragma solidity >=0.5.0 <0.8.0;

interface INodeInterface {
    function lookupMessageBatchProof(uint256 batchNum, uint64 index)
        external
        view
        returns (
            bytes32[] memory proof,
            uint256 path,
            address l2Sender,
            address l1Dest,
            uint256 l2Block,
            uint256 l1Block,
            uint256 timestamp,
            uint256 amount,
            bytes memory calldataForL1
        );
}