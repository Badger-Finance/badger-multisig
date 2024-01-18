// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IQuestBoard {
    function GAUGE_CONTROLLER() external view returns (address);

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

    function biasCalculator() external view returns (address);

    function closePartOfQuestPeriod(uint256 period, uint256[] memory questIDs)
        external
        returns (uint256 closed, uint256 skipped);

    function closeQuestPeriod(uint256 period)
        external
        returns (uint256 closed, uint256 skipped);

    function createFixedQuest(
        address gauge,
        address rewardToken,
        bool startNextPeriod,
        uint48 duration,
        uint256 rewardPerVote,
        uint256 totalRewardAmount,
        uint256 feeAmount,
        uint8 voteType,
        uint8 closeType,
        address[] memory voterList
    ) external returns (uint256);

    function createRangedQuest(
        address gauge,
        address rewardToken,
        bool startNextPeriod,
        uint48 duration,
        uint256 minRewardPerVote,
        uint256 maxRewardPerVote,
        uint256 totalRewardAmount,
        uint256 feeAmount,
        uint8 voteType,
        uint8 closeType,
        address[] memory voterList
    ) external returns (uint256);

    function customPlatformFeeRatio(address) external view returns (uint256);

    function distributor() external view returns (address);

    function emergencyWithdraw(uint256 questID, address recipient) external;

    function extendQuestDuration(
        uint256 questID,
        uint48 addedDuration,
        uint256 addedRewardAmount,
        uint256 feeAmount
    ) external;

    function fixQuestPeriodBias(
        uint256 period,
        uint256 questID,
        uint256 correctReducedBias
    ) external;

    function getAllPeriodsForQuestId(uint256 questId)
        external
        view
        returns (uint48[] memory);

    function getAllQuestPeriodsForQuestId(uint256 questId)
        external
        view
        returns (IQuestBoardStruct.QuestPeriod[] memory);

    function getCurrentPeriod() external view returns (uint256);

    function getCurrentReducedBias(uint256 questID)
        external
        view
        returns (uint256);

    function getQuestCreator(uint256 questID) external view returns (address);

    function getQuestIdsForPeriod(uint256 period)
        external
        view
        returns (uint256[] memory);

    function getQuestIdsForPeriodForGauge(address gauge, uint256 period)
        external
        view
        returns (uint256[] memory);

    function init(address _distributor, address _biasCalculator) external;

    function isKilled() external view returns (bool);

    function killBoard() external;

    function killTs() external view returns (uint256);

    function minRewardPerVotePerToken(address) external view returns (uint256);

    function nextID() external view returns (uint256);

    function objectiveMinimalThreshold() external view returns (uint256);

    function owner() external view returns (address);

    function pendingOwner() external view returns (address);

    function periodsByQuest(uint256, uint256)
        external
        view
        returns (
            uint256 rewardAmountPerPeriod,
            uint256 minRewardPerVote,
            uint256 maxRewardPerVote,
            uint256 minObjectiveVotes,
            uint256 maxObjectiveVotes,
            uint256 rewardAmountDistributed,
            uint48 periodStart,
            uint8 currentState
        );

    function platformFeeRatio() external view returns (uint256);

    function questChest() external view returns (address);

    function questDistributors(uint256) external view returns (address);

    function questWithdrawableAmount(uint256) external view returns (uint256);

    function quests(uint256)
        external
        view
        returns (
            address creator,
            address rewardToken,
            address gauge,
            uint48 duration,
            uint48 periodStart,
            uint256 totalRewardAmount,
            IQuestBoardStruct.QuestTypes memory types
        );

    function recoverERC20(address token) external returns (bool);

    function removeManager(address manager) external;

    function renounceOwnership() external;

    function setCustomFeeRatio(address user, uint256 customFeeRatio) external;

    function transferOwnership(address newOwner) external;

    function unkillBoard() external;

    function updateChest(address chest) external;

    function updateDistributor(address newDistributor) external;

    function updateMinObjective(uint256 newMinObjective) external;

    function updatePlatformFee(uint256 newFee) external;

    function updateQuestParameters(
        uint256 questID,
        uint256 newMinRewardPerVote,
        uint256 newMaxRewardPerVote,
        uint256 addedPeriodRewardAmount,
        uint256 addedTotalRewardAmount,
        uint256 feeAmount
    ) external;

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

interface IQuestBoardStruct {
    struct QuestPeriod {
        uint256 rewardAmountPerPeriod;
        uint256 minRewardPerVote;
        uint256 maxRewardPerVote;
        uint256 minObjectiveVotes;
        uint256 maxObjectiveVotes;
        uint256 rewardAmountDistributed;
        uint48 periodStart;
        uint8 currentState;
    }

    struct QuestTypes {
        uint8 voteType;
        uint8 rewardsType;
        uint8 closeType;
    }
}