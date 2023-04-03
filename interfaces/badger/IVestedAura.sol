// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

interface IVestedAura {
    event Paused(address account);
    event RedirectionFee(
        address indexed destination,
        address indexed token,
        uint256 amount,
        uint256 indexed blockNumber,
        uint256 timestamp
    );
    event RewardsCollected(address token, uint256 amount);
    event SetWithdrawalMaxDeviationThreshold(uint256 newMaxDeviationThreshold);
    event TokenRedirection(
        address indexed destination,
        address indexed token,
        uint256 amount,
        uint256 indexed blockNumber,
        uint256 timestamp
    );
    event TreeDistribution(
        address indexed token,
        uint256 amount,
        uint256 indexed blockNumber,
        uint256 timestamp
    );
    event Unpaused(address account);

    function AURA() external view returns (address);

    function AURABAL() external view returns (address);

    function AURABAL_BALETH_BPT_POOL_ID() external view returns (bytes32);

    function AURA_ETH_POOL_ID() external view returns (bytes32);

    function BAL() external view returns (address);

    function BALANCER_VAULT() external view returns (address);

    function BALETH_BPT() external view returns (address);

    function BAL_ETH_POOL_ID() external view returns (bytes32);

    function LOCKER() external view returns (address);

    function MAX_BPS() external view returns (uint256);

    function SNAPSHOT() external view returns (address);

    function WETH() external view returns (address);

    function __BaseStrategy_init(address _vault) external;

    function auraBalToBalEthBptMinOutBps() external view returns (uint256);

    function autoCompoundRatio() external view returns (uint256);

    function balanceOf() external view returns (uint256);

    function balanceOfPool() external view returns (uint256);

    function balanceOfRewards()
        external
        view
        returns (BaseStrategy.TokenAmount[] memory rewards);

    function balanceOfWant() external view returns (uint256);

    function baseStrategyVersion() external pure returns (string memory);

    function bribesProcessor() external view returns (address);

    function bribesRedirectionPaths(address) external view returns (address);

    function checkUpkeep(
        bytes calldata checkData
    ) external view returns (bool upkeepNeeded, bytes memory performData);

    function claimBribesFromHiddenHand(
        address hiddenHandDistributor,
        IRewardDistributor.Claim[] calldata _claims
    ) external;

    function clearSnapshotDelegate(bytes32 id) external;

    function deposit() external;

    function earn() external;

    function emitNonProtectedToken(address _token) external;

    function getAuraLockerDelegate() external view returns (address);

    function getDelegate() external view returns (address);

    function getName() external pure returns (string memory);

    function getProtectedTokens() external view returns (address[] memory);

    function getSnapshotDelegate(bytes32 id) external view returns (address);

    function governance() external view returns (address);

    function guardian() external view returns (address);

    function harvest()
        external
        returns (BaseStrategy.TokenAmount[] memory harvested);

    function initialize(address _vault) external;

    function isProtectedToken(address token) external view returns (bool);

    function isTendable() external pure returns (bool);

    function keeper() external view returns (address);

    function manualProcessExpiredLocks() external;

    function manualSendAuraToVault() external;

    function pause() external;

    function paused() external view returns (bool);

    function performUpkeep(bytes calldata performData) external;

    function prepareWithdrawAll() external;

    function processLocksOnReinvest() external view returns (bool);

    function redirectionFees(address) external view returns (uint256);

    function reinvest() external returns (uint256);

    function setAuraBalToBalEthBptMinOutBps(uint256 _minOutBps) external;

    function setAuraLockerDelegate(address delegate) external;

    function setBribesProcessor(address newBribesProcessor) external;

    function setProcessLocksOnReinvest(bool newProcessLocksOnReinvest) external;

    function setRedirectionToken(
        address token,
        address recepient,
        uint256 redirectionFee
    ) external;

    function setSnapshotDelegate(bytes32 id, address delegate) external;

    function setWithdrawalMaxDeviationThreshold(uint256 _threshold) external;

    function setWithdrawalSafetyCheck(bool newWithdrawalSafetyCheck) external;

    function strategist() external view returns (address);

    function sweepRewardToken(address token) external;

    function sweepRewards(address[] calldata tokens) external;

    function tend() external returns (BaseStrategy.TokenAmount[] memory tended);

    function unpause() external;

    function vault() external view returns (address);

    function version() external pure returns (string memory);

    function want() external view returns (address);

    function withdraw(uint256 _amount) external;

    function withdrawOther(address _asset) external;

    function withdrawToVault() external;

    function withdrawalMaxDeviationThreshold() external view returns (uint256);

    function withdrawalSafetyCheck() external view returns (bool);

    receive() external payable;
}

interface BaseStrategy {
    struct TokenAmount {
        address token;
        uint256 amount;
    }
}

interface IRewardDistributor {
    struct Claim {
        bytes32 identifier;
        address account;
        uint256 amount;
        bytes32[] merkleProof;
    }
}
