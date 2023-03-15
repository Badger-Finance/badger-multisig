// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

interface IKeeperRegistry {
    error ArrayHasNoEntries();
    error CannotCancel();
    error DuplicateEntry();
    error GasLimitCanOnlyIncrease();
    error GasLimitOutsideRange();
    error IndexOutOfRange();
    error InsufficientFunds();
    error InvalidDataLength();
    error InvalidPayee();
    error InvalidRecipient();
    error KeepersMustTakeTurns();
    error MigrationNotPermitted();
    error NotAContract();
    error OnlyActiveKeepers();
    error OnlyCallableByAdmin();
    error OnlyCallableByLINKToken();
    error OnlyCallableByOwnerOrAdmin();
    error OnlyCallableByOwnerOrRegistrar();
    error OnlyCallableByPayee();
    error OnlyCallableByProposedPayee();
    error OnlySimulatedBackend();
    error ParameterLengthError();
    error PaymentGreaterThanAllLINK();
    error TargetCheckReverted(bytes reason);
    error TranscoderNotSet();
    error UpkeepNotActive();
    error UpkeepNotCanceled();
    error UpkeepNotNeeded();
    error ValueNotChanged();
    event ConfigSet(Config config);
    event FundsAdded(uint256 indexed id, address indexed from, uint96 amount);
    event FundsWithdrawn(uint256 indexed id, uint256 amount, address to);
    event KeepersUpdated(address[] keepers, address[] payees);
    event OwnerFundsWithdrawn(uint96 amount);
    event OwnershipTransferRequested(address indexed from, address indexed to);
    event OwnershipTransferred(address indexed from, address indexed to);
    event Paused(address account);
    event PayeeshipTransferRequested(
        address indexed keeper,
        address indexed from,
        address indexed to
    );
    event PayeeshipTransferred(
        address indexed keeper,
        address indexed from,
        address indexed to
    );
    event PaymentWithdrawn(
        address indexed keeper,
        uint256 indexed amount,
        address indexed to,
        address payee
    );
    event Unpaused(address account);
    event UpkeepCanceled(uint256 indexed id, uint64 indexed atBlockHeight);
    event UpkeepGasLimitSet(uint256 indexed id, uint96 gasLimit);
    event UpkeepMigrated(
        uint256 indexed id,
        uint256 remainingBalance,
        address destination
    );
    event UpkeepPerformed(
        uint256 indexed id,
        bool indexed success,
        address indexed from,
        uint96 payment,
        bytes performData
    );
    event UpkeepReceived(
        uint256 indexed id,
        uint256 startingBalance,
        address importedFrom
    );
    event UpkeepRegistered(
        uint256 indexed id,
        uint32 executeGas,
        address admin
    );

    function FAST_GAS_FEED() external view returns (address);

    function LINK() external view returns (address);

    function LINK_ETH_FEED() external view returns (address);

    function acceptOwnership() external;

    function acceptPayeeship(address keeper) external;

    function addFunds(uint256 id, uint96 amount) external;

    function cancelUpkeep(uint256 id) external;

    function checkUpkeep(uint256 id, address from)
        external
        returns (
            bytes memory performData,
            uint256 maxLinkPayment,
            uint256 gasLimit,
            uint256 adjustedGasWei,
            uint256 linkEth
        );

    function getActiveUpkeepIDs(uint256 startIndex, uint256 maxCount)
        external
        view
        returns (uint256[] memory);

    function getKeeperInfo(address query)
        external
        view
        returns (
            address payee,
            bool active,
            uint96 balance
        );

    function getMaxPaymentForGas(uint256 gasLimit)
        external
        view
        returns (uint96 maxPayment);

    function getMinBalanceForUpkeep(uint256 id)
        external
        view
        returns (uint96 minBalance);

    function getPeerRegistryMigrationPermission(address peer)
        external
        view
        returns (uint8);

    function getState()
        external
        view
        returns (
            State memory state,
            Config memory config,
            address[] memory keepers
        );

    function getUpkeep(uint256 id)
        external
        view
        returns (
            address target,
            uint32 executeGas,
            bytes memory checkData,
            uint96 balance,
            address lastKeeper,
            address admin,
            uint64 maxValidBlocknumber,
            uint96 amountSpent
        );

    function migrateUpkeeps(uint256[] memory ids, address destination) external;

    function onTokenTransfer(
        address sender,
        uint256 amount,
        bytes memory data
    ) external;

    function owner() external view returns (address);

    function pause() external;

    function paused() external view returns (bool);

    function performUpkeep(uint256 id, bytes memory performData)
        external
        returns (bool success);

    function receiveUpkeeps(bytes memory encodedUpkeeps) external;

    function recoverFunds() external;

    function registerUpkeep(
        address target,
        uint32 gasLimit,
        address admin,
        bytes memory checkData
    ) external returns (uint256 id);

    function setConfig(Config memory config) external;

    function setKeepers(address[] memory keepers, address[] memory payees)
        external;

    function setPeerRegistryMigrationPermission(address peer, uint8 permission)
        external;

    function setUpkeepGasLimit(uint256 id, uint32 gasLimit) external;

    function transferOwnership(address to) external;

    function transferPayeeship(address keeper, address proposed) external;

    function typeAndVersion() external view returns (string memory);

    function unpause() external;

    function upkeepTranscoderVersion() external view returns (uint8);

    function withdrawFunds(uint256 id, address to) external;

    function withdrawOwnerFunds() external;

    function withdrawPayment(address from, address to) external;
}

struct Config {
    uint32 paymentPremiumPPB;
    uint32 flatFeeMicroLink;
    uint24 blockCountPerTurn;
    uint32 checkGasLimit;
    uint24 stalenessSeconds;
    uint16 gasCeilingMultiplier;
    uint96 minUpkeepSpend;
    uint32 maxPerformGas;
    uint256 fallbackGasPrice;
    uint256 fallbackLinkPrice;
    address transcoder;
    address registrar;
}

struct State {
    uint32 nonce;
    uint96 ownerLinkBalance;
    uint256 expectedLinkBalance;
    uint256 numUpkeeps;
}
