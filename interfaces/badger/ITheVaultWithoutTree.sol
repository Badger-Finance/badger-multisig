// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

interface ITheVaultWithoutTree {
    event Approval(
        address indexed owner,
        address indexed spender,
        uint256 value
    );
    event Harvested(
        address indexed token,
        uint256 amount,
        uint256 indexed blockNumber,
        uint256 timestamp
    );
    event PauseDeposits(address indexed pausedBy);
    event Paused(address account);
    event SetGuardian(address indexed newGuardian);
    event SetGuestList(address indexed newGuestList);
    event SetManagementFee(uint256 newManagementFee);
    event SetMaxManagementFee(uint256 newMaxManagementFee);
    event SetMaxPerformanceFee(uint256 newMaxPerformanceFee);
    event SetMaxWithdrawalFee(uint256 newMaxWithdrawalFee);
    event SetPerformanceFeeGovernance(uint256 newPerformanceFeeGovernance);
    event SetPerformanceFeeStrategist(uint256 newPerformanceFeeStrategist);
    event SetStrategy(address indexed newStrategy);
    event SetToEarnBps(uint256 newEarnToBps);
    event SetTreasury(address indexed newTreasury);
    event SetWithdrawalFee(uint256 newWithdrawalFee);
    event Transfer(address indexed from, address indexed to, uint256 value);
    event TreeDistribution(
        address indexed token,
        uint256 amount,
        uint256 indexed blockNumber,
        uint256 timestamp
    );
    event UnpauseDeposits(address indexed pausedBy);
    event Unpaused(address account);

    function MANAGEMENT_FEE_HARD_CAP() external view returns (uint256);

    function MAX_BPS() external view returns (uint256);

    function PERFORMANCE_FEE_HARD_CAP() external view returns (uint256);

    function SECS_PER_YEAR() external view returns (uint256);

    function WITHDRAWAL_FEE_HARD_CAP() external view returns (uint256);

    function additionalTokensEarned(address) external view returns (uint256);

    function allowance(address owner, address spender)
        external
        view
        returns (uint256);

    function approve(address spender, uint256 amount) external returns (bool);

    function assetsAtLastHarvest() external view returns (uint256);

    function available() external view returns (uint256);

    function badgerTree() external view returns (address);

    function balance() external view returns (uint256);

    function balanceOf(address account) external view returns (uint256);

    function decimals() external view returns (uint8);

    function decreaseAllowance(address spender, uint256 subtractedValue)
        external
        returns (bool);

    function deposit(uint256 _amount, bytes32[] memory proof) external;

    function deposit(uint256 _amount) external;

    function depositAll(bytes32[] memory proof) external;

    function depositAll() external;

    function depositFor(address _recipient, uint256 _amount) external;

    function depositFor(
        address _recipient,
        uint256 _amount,
        bytes32[] memory proof
    ) external;

    function earn() external;

    function emitNonProtectedToken(address _token) external;

    function getPricePerFullShare() external view returns (uint256);

    function governance() external view returns (address);

    function guardian() external view returns (address);

    function guestList() external view returns (address);

    function increaseAllowance(address spender, uint256 addedValue)
        external
        returns (bool);

    function initialize(
        address _token,
        address _governance,
        address _keeper,
        address _guardian,
        address _treasury,
        address _strategist,
        address _badgerTree,
        string memory _name,
        string memory _symbol,
        uint256[4] memory _feeConfig
    ) external;

    function keeper() external view returns (address);

    function lastAdditionalTokenAmount(address) external view returns (uint256);

    function lastHarvestAmount() external view returns (uint256);

    function lastHarvestedAt() external view returns (uint256);

    function lifeTimeEarned() external view returns (uint256);

    function managementFee() external view returns (uint256);

    function maxManagementFee() external view returns (uint256);

    function maxPerformanceFee() external view returns (uint256);

    function maxWithdrawalFee() external view returns (uint256);

    function name() external view returns (string memory);

    function pause() external;

    function pauseDeposits() external;

    function paused() external view returns (bool);

    function pausedDeposit() external view returns (bool);

    function performanceFeeGovernance() external view returns (uint256);

    function performanceFeeStrategist() external view returns (uint256);

    function reportAdditionalToken(address _token) external;

    function reportHarvest(uint256 _harvestedAmount) external;

    function setGovernance(address _governance) external;

    function setGuardian(address _guardian) external;

    function setGuestList(address _guestList) external;

    function setKeeper(address _keeper) external;

    function setManagementFee(uint256 _fees) external;

    function setMaxManagementFee(uint256 _fees) external;

    function setMaxPerformanceFee(uint256 _fees) external;

    function setMaxWithdrawalFee(uint256 _fees) external;

    function setPerformanceFeeGovernance(uint256 _performanceFeeGovernance)
        external;

    function setPerformanceFeeStrategist(uint256 _performanceFeeStrategist)
        external;

    function setStrategist(address _strategist) external;

    function setStrategy(address _strategy) external;

    function setToEarnBps(uint256 _newToEarnBps) external;

    function setTreasury(address _treasury) external;

    function setWithdrawalFee(uint256 _withdrawalFee) external;

    function strategist() external view returns (address);

    function strategy() external view returns (address);

    function sweepExtraToken(address _token) external;

    function symbol() external view returns (string memory);

    function toEarnBps() external view returns (uint256);

    function token() external view returns (address);

    function totalSupply() external view returns (uint256);

    function transfer(address recipient, uint256 amount)
        external
        returns (bool);

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) external returns (bool);

    function treasury() external view returns (address);

    function unpause() external;

    function unpauseDeposits() external;

    function version() external pure returns (string memory);

    function withdraw(uint256 _shares) external;

    function withdrawAll() external;

    function withdrawToVault() external;

    function withdrawalFee() external view returns (uint256);
}