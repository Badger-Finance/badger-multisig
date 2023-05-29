
// SPDX-License-Identifier: agpl-3.0
pragma solidity 0.7.5;
pragma experimental ABIEncoderV2;

interface IStakedTokenV2Rev3 {
    event Approval(
        address indexed owner,
        address indexed spender,
        uint256 value
    );
    event AssetConfigUpdated(address indexed asset, uint256 emission);
    event AssetIndexUpdated(address indexed asset, uint256 index);
    event Cooldown(address indexed user);
    event DelegateChanged(
        address indexed delegator,
        address indexed delegatee,
        uint8 delegationType
    );
    event DelegatedPowerChanged(
        address indexed user,
        uint256 amount,
        uint8 delegationType
    );
    event Redeem(address indexed from, address indexed to, uint256 amount);
    event RewardsAccrued(address user, uint256 amount);
    event RewardsClaimed(
        address indexed from,
        address indexed to,
        uint256 amount
    );
    event Staked(
        address indexed from,
        address indexed onBehalfOf,
        uint256 amount
    );
    event Transfer(address indexed from, address indexed to, uint256 value);
    event UserIndexUpdated(
        address indexed user,
        address indexed asset,
        uint256 index
    );

    function COOLDOWN_SECONDS() external view returns (uint256);

    function DELEGATE_BY_TYPE_TYPEHASH() external view returns (bytes32);

    function DELEGATE_TYPEHASH() external view returns (bytes32);

    function DISTRIBUTION_END() external view returns (uint256);

    function DOMAIN_SEPARATOR() external view returns (bytes32);

    function EIP712_REVISION() external view returns (bytes memory);

    function EMISSION_MANAGER() external view returns (address);

    function PERMIT_TYPEHASH() external view returns (bytes32);

    function PRECISION() external view returns (uint8);

    function REVISION() external view returns (uint256);

    function REWARDS_VAULT() external view returns (address);

    function REWARD_TOKEN() external view returns (address);

    function STAKED_TOKEN() external view returns (address);

    function UNSTAKE_WINDOW() external view returns (uint256);

    function _aaveGovernance() external view returns (address);

    function _nonces(address) external view returns (uint256);

    function _votingSnapshots(address, uint256)
        external
        view
        returns (uint128 blockNumber, uint128 value);

    function _votingSnapshotsCounts(address) external view returns (uint256);

    function allowance(address owner, address spender)
        external
        view
        returns (uint256);

    function approve(address spender, uint256 amount) external returns (bool);

    function assets(address)
        external
        view
        returns (
            uint128 emissionPerSecond,
            uint128 lastUpdateTimestamp,
            uint256 index
        );

    function balanceOf(address account) external view returns (uint256);

    function claimRewards(address to, uint256 amount) external;

    function configureAssets(
        DistributionTypes.AssetConfigInput[] memory assetsConfigInput
    ) external;

    function cooldown() external;

    function decimals() external view returns (uint8);

    function decreaseAllowance(address spender, uint256 subtractedValue)
        external
        returns (bool);

    function delegate(address delegatee) external;

    function delegateBySig(
        address delegatee,
        uint256 nonce,
        uint256 expiry,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;

    function delegateByType(address delegatee, uint8 delegationType) external;

    function delegateByTypeBySig(
        address delegatee,
        uint8 delegationType,
        uint256 nonce,
        uint256 expiry,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;

    function getDelegateeByType(address delegator, uint8 delegationType)
        external
        view
        returns (address);

    function getNextCooldownTimestamp(
        uint256 fromCooldownTimestamp,
        uint256 amountToReceive,
        address toAddress,
        uint256 toBalance
    ) external view returns (uint256);

    function getPowerAtBlock(
        address user,
        uint256 blockNumber,
        uint8 delegationType
    ) external view returns (uint256);

    function getPowerCurrent(address user, uint8 delegationType)
        external
        view
        returns (uint256);

    function getTotalRewardsBalance(address staker)
        external
        view
        returns (uint256);

    function getUserAssetData(address user, address asset)
        external
        view
        returns (uint256);

    function increaseAllowance(address spender, uint256 addedValue)
        external
        returns (bool);

    function initialize() external;

    function name() external view returns (string memory);

    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;

    function redeem(address to, uint256 amount) external;

    function stake(address onBehalfOf, uint256 amount) external;

    function stakerRewardsToClaim(address) external view returns (uint256);

    function stakersCooldowns(address) external view returns (uint256);

    function symbol() external view returns (string memory);

    function totalSupply() external view returns (uint256);

    function totalSupplyAt(uint256 blockNumber) external view returns (uint256);

    function transfer(address recipient, uint256 amount)
        external
        returns (bool);

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) external returns (bool);
}

interface DistributionTypes {
    struct AssetConfigInput {
        uint128 emissionPerSecond;
        uint256 totalStaked;
        address underlyingAsset;
    }
}
