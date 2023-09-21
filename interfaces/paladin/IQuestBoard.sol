// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IQuestBoard {
    function GAUGE_CONTROLLER() external view returns (address);

    function KILL_DELAY() external view returns (uint256);

    function acceptOwnership() external;

    function addMerkleRoot(
        uint256 questID,
        uint256 period,
        uint256 totalAmount,
        bytes32 merkleRoot
    ) external;

    function addMultipleMerkleRoot(
        uint256[] memory questIDs,
        uint256 period,
        uint256[] memory totalAmounts,
        bytes32[] memory merkleRoots
    ) external;

    function approveManager(address newManager) external;

    function closePartOfQuestPeriod(uint256 period, uint256[] memory questIDs)
        external
        returns (uint256 closed, uint256 skipped);

    function closeQuestPeriod(uint256 period)
        external
        returns (uint256 closed, uint256 skipped);

    function createQuest(
        address gauge,
        address rewardToken,
        uint48 duration,
        uint256 objective,
        uint256 rewardPerVote,
        uint256 totalRewardAmount,
        uint256 feeAmount
    ) external returns (uint256);

    function distributor() external view returns (address);

    function emergencyWithdraw(uint256 questID, address recipient) external;

    function getAllPeriodsForQuestId(uint256 questId)
        external
        view
        returns (uint48[] memory);

    function getAllQuestPeriodsForQuestId(uint256 questId)
        external
        view
        returns (QuestBoard.QuestPeriod[] memory);

    function getCurrentPeriod() external view returns (uint256);

    function getQuestIdsForPeriod(uint256 period)
        external
        view
        returns (uint256[] memory);

    function increaseQuestDuration(
        uint256 questID,
        uint48 addedDuration,
        uint256 addedRewardAmount,
        uint256 feeAmount
    ) external;

    function increaseQuestObjective(
        uint256 questID,
        uint256 newObjective,
        uint256 addedRewardAmount,
        uint256 feeAmount
    ) external;

    function increaseQuestReward(
        uint256 questID,
        uint256 newRewardPerVote,
        uint256 addedRewardAmount,
        uint256 feeAmount
    ) external;

    function initiateDistributor(address newDistributor) external;

    function isKilled() external view returns (bool);

    function killBoard() external;

    function kill_ts() external view returns (uint256);

    function minObjective() external view returns (uint256);

    function minRewardPerVotePerToken(address) external view returns (uint256);

    function nextID() external view returns (uint256);

    function owner() external view returns (address);

    function pendingOwner() external view returns (address);

    function periodsByQuest(uint256, uint256)
        external
        view
        returns (
            uint256 rewardAmountPerPeriod,
            uint256 rewardPerVote,
            uint256 objectiveVotes,
            uint256 rewardAmountDistributed,
            uint256 withdrawableAmount,
            uint48 periodStart,
            uint8 currentState
        );

    function platformFee() external view returns (uint256);

    function questChest() external view returns (address);

    function questDistributors(uint256) external view returns (address);

    function questPeriods(uint256, uint256) external view returns (uint48);

    function quests(uint256)
        external
        view
        returns (
            address creator,
            address rewardToken,
            address gauge,
            uint48 duration,
            uint48 periodStart,
            uint256 totalRewardAmount
        );

    function questsByPeriod(uint256, uint256) external view returns (uint256);

    function recoverERC20(address token) external returns (bool);

    function removeManager(address manager) external;

    function renounceOwnership() external;

    function transferOwnership(address newOwner) external;

    function unkillBoard() external;

    function updateChest(address chest) external;

    function updateDistributor(address newDistributor) external;

    function updateMinObjective(uint256 newMinObjective) external;

    function updatePlatformFee(uint256 newFee) external;

    function updateRewardToken(address newToken, uint256 newMinRewardPerVote)
        external;

    function whitelistMultipleTokens(
        address[] memory newTokens,
        uint256[] memory minRewardPerVotes
    ) external;

    function whitelistToken(address newToken, uint256 minRewardPerVote)
        external;

    function whitelistedTokens(address) external view returns (bool);

    function withdrawUnusedRewards(uint256 questID, address recipient) external;
}

interface QuestBoard {
    struct QuestPeriod {
        uint256 rewardAmountPerPeriod;
        uint256 rewardPerVote;
        uint256 objectiveVotes;
        uint256 rewardAmountDistributed;
        uint256 withdrawableAmount;
        uint48 periodStart;
        uint8 currentState;
    }
}