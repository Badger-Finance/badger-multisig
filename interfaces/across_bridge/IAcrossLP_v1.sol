// SPDX-License-Identifier: MIT
pragma solidity >=0.5.0 <0.8.0;
pragma experimental ABIEncoderV2;

interface IAcrossLP_v1 {
    event Approval(
        address indexed owner,
        address indexed spender,
        uint256 value
    );
    event BridgePoolAdminTransferred(address oldAdmin, address newAdmin);
    event DepositRelayed(
        bytes32 indexed depositHash,
        BridgePool.DepositData depositData,
        BridgePool.RelayData relay,
        bytes32 relayAncillaryDataHash
    );
    event LiquidityAdded(
        uint256 amount,
        uint256 lpTokensMinted,
        address indexed liquidityProvider
    );
    event LiquidityRemoved(
        uint256 amount,
        uint256 lpTokensBurnt,
        address indexed liquidityProvider
    );
    event RelayCanceled(
        bytes32 indexed depositHash,
        bytes32 indexed relayHash,
        address indexed disputer
    );
    event RelayDisputed(
        bytes32 indexed depositHash,
        bytes32 indexed relayHash,
        address indexed disputer
    );
    event RelaySettled(
        bytes32 indexed depositHash,
        address indexed caller,
        BridgePool.RelayData relay
    );
    event RelaySpedUp(
        bytes32 indexed depositHash,
        address indexed instantRelayer,
        BridgePool.RelayData relay
    );
    event Transfer(address indexed from, address indexed to, uint256 value);

    function addLiquidity(uint256 l1TokenAmount) external payable;

    function allowance(address owner, address spender)
        external
        view
        returns (uint256);

    function approve(address spender, uint256 amount) external returns (bool);

    function balanceOf(address account) external view returns (uint256);

    function bonds() external view returns (uint256);

    function bridgeAdmin() external view returns (address);

    function changeAdmin(address _newAdmin) external;

    function decimals() external view returns (uint8);

    function decreaseAllowance(address spender, uint256 subtractedValue)
        external
        returns (bool);

    function disputeRelay(
        BridgePool.DepositData memory depositData,
        BridgePool.RelayData memory relayData
    ) external;

    function exchangeRateCurrent() external returns (uint256);

    function getAccumulatedFees() external view returns (uint256);

    function getCurrentTime() external view returns (uint256);

    function getLiquidityUtilization(uint256 relayedAmount)
        external
        returns (uint256 utilizationCurrent, uint256 utilizationPostRelay);

    function getRelayAncillaryData(
        BridgePool.DepositData memory depositData,
        BridgePool.RelayData memory relayData
    ) external view returns (bytes memory);

    function identifier() external view returns (bytes32);

    function increaseAllowance(address spender, uint256 addedValue)
        external
        returns (bool);

    function instantRelays(bytes32) external view returns (address);

    function isWethPool() external view returns (bool);

    function l1Token() external view returns (address);

    function lastLpFeeUpdate() external view returns (uint32);

    function liquidReserves() external view returns (uint256);

    function liquidityUtilizationCurrent() external returns (uint256);

    function liquidityUtilizationPostRelay(uint256 relayedAmount)
        external
        returns (uint256);

    function lpFeeRatePerSecond() external view returns (uint64);

    function multicall(bytes[] memory data)
        external
        payable
        returns (bytes[] memory results);

    function name() external view returns (string memory);

    function numberOfRelays() external view returns (uint32);

    function optimisticOracle() external view returns (address);

    function optimisticOracleLiveness() external view returns (uint32);

    function pendingReserves() external view returns (uint256);

    function proposerBondPct() external view returns (uint64);

    function relayAndSpeedUp(
        BridgePool.DepositData memory depositData,
        uint64 realizedLpFeePct
    ) external;

    function relayDeposit(
        BridgePool.DepositData memory depositData,
        uint64 realizedLpFeePct
    ) external;

    function relays(bytes32) external view returns (bytes32);

    function removeLiquidity(uint256 lpTokenAmount, bool sendEth) external;

    function setCurrentTime(uint256 time) external;

    function settleRelay(
        BridgePool.DepositData memory depositData,
        BridgePool.RelayData memory relayData
    ) external;

    function speedUpRelay(
        BridgePool.DepositData memory depositData,
        BridgePool.RelayData memory relayData
    ) external;

    function store() external view returns (address);

    function symbol() external view returns (string memory);

    function sync() external;

    function syncUmaEcosystemParams() external;

    function syncWithBridgeAdminParams() external;

    function timerAddress() external view returns (address);

    function totalSupply() external view returns (uint256);

    function transfer(address recipient, uint256 amount)
        external
        returns (bool);

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) external returns (bool);

    function undistributedLpFees() external view returns (uint256);

    function utilizedReserves() external view returns (int256);

    receive() external payable;
}

interface BridgePool {
    struct DepositData {
        uint256 chainId;
        uint64 depositId;
        address l1Recipient;
        address l2Sender;
        uint256 amount;
        uint64 slowRelayFeePct;
        uint64 instantRelayFeePct;
        uint32 quoteTimestamp;
    }

    struct RelayData {
        uint8 relayState;
        address slowRelayer;
        uint32 relayId;
        uint64 realizedLpFeePct;
        uint32 priceRequestTime;
        uint256 proposerBond;
        uint256 finalFee;
    }
}

// THIS FILE WAS AUTOGENERATED FROM THE FOLLOWING ABI JSON:
/*
[{"inputs":[{"internalType":"string","name":"_lpTokenName","type":"string"},{"internalType":"string","name":"_lpTokenSymbol","type":"string"},{"internalType":"address","name":"_bridgeAdmin","type":"address"},{"internalType":"address","name":"_l1Token","type":"address"},{"internalType":"uint64","name":"_lpFeeRatePerSecond","type":"uint64"},{"internalType":"bool","name":"_isWethPool","type":"bool"},{"internalType":"address","name":"_timer","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"oldAdmin","type":"address"},{"indexed":false,"internalType":"address","name":"newAdmin","type":"address"}],"name":"BridgePoolAdminTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"depositHash","type":"bytes32"},{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"uint64","name":"depositId","type":"uint64"},{"internalType":"address payable","name":"l1Recipient","type":"address"},{"internalType":"address","name":"l2Sender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint64","name":"slowRelayFeePct","type":"uint64"},{"internalType":"uint64","name":"instantRelayFeePct","type":"uint64"},{"internalType":"uint32","name":"quoteTimestamp","type":"uint32"}],"indexed":false,"internalType":"struct BridgePool.DepositData","name":"depositData","type":"tuple"},{"components":[{"internalType":"enum BridgePool.RelayState","name":"relayState","type":"uint8"},{"internalType":"address","name":"slowRelayer","type":"address"},{"internalType":"uint32","name":"relayId","type":"uint32"},{"internalType":"uint64","name":"realizedLpFeePct","type":"uint64"},{"internalType":"uint32","name":"priceRequestTime","type":"uint32"},{"internalType":"uint256","name":"proposerBond","type":"uint256"},{"internalType":"uint256","name":"finalFee","type":"uint256"}],"indexed":false,"internalType":"struct BridgePool.RelayData","name":"relay","type":"tuple"},{"indexed":false,"internalType":"bytes32","name":"relayAncillaryDataHash","type":"bytes32"}],"name":"DepositRelayed","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"lpTokensMinted","type":"uint256"},{"indexed":true,"internalType":"address","name":"liquidityProvider","type":"address"}],"name":"LiquidityAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"lpTokensBurnt","type":"uint256"},{"indexed":true,"internalType":"address","name":"liquidityProvider","type":"address"}],"name":"LiquidityRemoved","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"depositHash","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"relayHash","type":"bytes32"},{"indexed":true,"internalType":"address","name":"disputer","type":"address"}],"name":"RelayCanceled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"depositHash","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"relayHash","type":"bytes32"},{"indexed":true,"internalType":"address","name":"disputer","type":"address"}],"name":"RelayDisputed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"depositHash","type":"bytes32"},{"indexed":true,"internalType":"address","name":"caller","type":"address"},{"components":[{"internalType":"enum BridgePool.RelayState","name":"relayState","type":"uint8"},{"internalType":"address","name":"slowRelayer","type":"address"},{"internalType":"uint32","name":"relayId","type":"uint32"},{"internalType":"uint64","name":"realizedLpFeePct","type":"uint64"},{"internalType":"uint32","name":"priceRequestTime","type":"uint32"},{"internalType":"uint256","name":"proposerBond","type":"uint256"},{"internalType":"uint256","name":"finalFee","type":"uint256"}],"indexed":false,"internalType":"struct BridgePool.RelayData","name":"relay","type":"tuple"}],"name":"RelaySettled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"depositHash","type":"bytes32"},{"indexed":true,"internalType":"address","name":"instantRelayer","type":"address"},{"components":[{"internalType":"enum BridgePool.RelayState","name":"relayState","type":"uint8"},{"internalType":"address","name":"slowRelayer","type":"address"},{"internalType":"uint32","name":"relayId","type":"uint32"},{"internalType":"uint64","name":"realizedLpFeePct","type":"uint64"},{"internalType":"uint32","name":"priceRequestTime","type":"uint32"},{"internalType":"uint256","name":"proposerBond","type":"uint256"},{"internalType":"uint256","name":"finalFee","type":"uint256"}],"indexed":false,"internalType":"struct BridgePool.RelayData","name":"relay","type":"tuple"}],"name":"RelaySpedUp","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"uint256","name":"l1TokenAmount","type":"uint256"}],"name":"addLiquidity","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"bonds","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"bridgeAdmin","outputs":[{"internalType":"contract BridgeAdminInterface","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_newAdmin","type":"address"}],"name":"changeAdmin","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"uint64","name":"depositId","type":"uint64"},{"internalType":"address payable","name":"l1Recipient","type":"address"},{"internalType":"address","name":"l2Sender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint64","name":"slowRelayFeePct","type":"uint64"},{"internalType":"uint64","name":"instantRelayFeePct","type":"uint64"},{"internalType":"uint32","name":"quoteTimestamp","type":"uint32"}],"internalType":"struct BridgePool.DepositData","name":"depositData","type":"tuple"},{"components":[{"internalType":"enum BridgePool.RelayState","name":"relayState","type":"uint8"},{"internalType":"address","name":"slowRelayer","type":"address"},{"internalType":"uint32","name":"relayId","type":"uint32"},{"internalType":"uint64","name":"realizedLpFeePct","type":"uint64"},{"internalType":"uint32","name":"priceRequestTime","type":"uint32"},{"internalType":"uint256","name":"proposerBond","type":"uint256"},{"internalType":"uint256","name":"finalFee","type":"uint256"}],"internalType":"struct BridgePool.RelayData","name":"relayData","type":"tuple"}],"name":"disputeRelay","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"exchangeRateCurrent","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getAccumulatedFees","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getCurrentTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"relayedAmount","type":"uint256"}],"name":"getLiquidityUtilization","outputs":[{"internalType":"uint256","name":"utilizationCurrent","type":"uint256"},{"internalType":"uint256","name":"utilizationPostRelay","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"uint64","name":"depositId","type":"uint64"},{"internalType":"address payable","name":"l1Recipient","type":"address"},{"internalType":"address","name":"l2Sender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint64","name":"slowRelayFeePct","type":"uint64"},{"internalType":"uint64","name":"instantRelayFeePct","type":"uint64"},{"internalType":"uint32","name":"quoteTimestamp","type":"uint32"}],"internalType":"struct BridgePool.DepositData","name":"depositData","type":"tuple"},{"components":[{"internalType":"enum BridgePool.RelayState","name":"relayState","type":"uint8"},{"internalType":"address","name":"slowRelayer","type":"address"},{"internalType":"uint32","name":"relayId","type":"uint32"},{"internalType":"uint64","name":"realizedLpFeePct","type":"uint64"},{"internalType":"uint32","name":"priceRequestTime","type":"uint32"},{"internalType":"uint256","name":"proposerBond","type":"uint256"},{"internalType":"uint256","name":"finalFee","type":"uint256"}],"internalType":"struct BridgePool.RelayData","name":"relayData","type":"tuple"}],"name":"getRelayAncillaryData","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"identifier","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"instantRelays","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"isWethPool","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"l1Token","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lastLpFeeUpdate","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"liquidReserves","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"liquidityUtilizationCurrent","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"relayedAmount","type":"uint256"}],"name":"liquidityUtilizationPostRelay","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"lpFeeRatePerSecond","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes[]","name":"data","type":"bytes[]"}],"name":"multicall","outputs":[{"internalType":"bytes[]","name":"results","type":"bytes[]"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"numberOfRelays","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"optimisticOracle","outputs":[{"internalType":"contract SkinnyOptimisticOracleInterface","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"optimisticOracleLiveness","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pendingReserves","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"proposerBondPct","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"uint64","name":"depositId","type":"uint64"},{"internalType":"address payable","name":"l1Recipient","type":"address"},{"internalType":"address","name":"l2Sender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint64","name":"slowRelayFeePct","type":"uint64"},{"internalType":"uint64","name":"instantRelayFeePct","type":"uint64"},{"internalType":"uint32","name":"quoteTimestamp","type":"uint32"}],"internalType":"struct BridgePool.DepositData","name":"depositData","type":"tuple"},{"internalType":"uint64","name":"realizedLpFeePct","type":"uint64"}],"name":"relayAndSpeedUp","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"uint64","name":"depositId","type":"uint64"},{"internalType":"address payable","name":"l1Recipient","type":"address"},{"internalType":"address","name":"l2Sender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint64","name":"slowRelayFeePct","type":"uint64"},{"internalType":"uint64","name":"instantRelayFeePct","type":"uint64"},{"internalType":"uint32","name":"quoteTimestamp","type":"uint32"}],"internalType":"struct BridgePool.DepositData","name":"depositData","type":"tuple"},{"internalType":"uint64","name":"realizedLpFeePct","type":"uint64"}],"name":"relayDeposit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"relays","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"lpTokenAmount","type":"uint256"},{"internalType":"bool","name":"sendEth","type":"bool"}],"name":"removeLiquidity","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"time","type":"uint256"}],"name":"setCurrentTime","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"uint64","name":"depositId","type":"uint64"},{"internalType":"address payable","name":"l1Recipient","type":"address"},{"internalType":"address","name":"l2Sender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint64","name":"slowRelayFeePct","type":"uint64"},{"internalType":"uint64","name":"instantRelayFeePct","type":"uint64"},{"internalType":"uint32","name":"quoteTimestamp","type":"uint32"}],"internalType":"struct BridgePool.DepositData","name":"depositData","type":"tuple"},{"components":[{"internalType":"enum BridgePool.RelayState","name":"relayState","type":"uint8"},{"internalType":"address","name":"slowRelayer","type":"address"},{"internalType":"uint32","name":"relayId","type":"uint32"},{"internalType":"uint64","name":"realizedLpFeePct","type":"uint64"},{"internalType":"uint32","name":"priceRequestTime","type":"uint32"},{"internalType":"uint256","name":"proposerBond","type":"uint256"},{"internalType":"uint256","name":"finalFee","type":"uint256"}],"internalType":"struct BridgePool.RelayData","name":"relayData","type":"tuple"}],"name":"settleRelay","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"uint64","name":"depositId","type":"uint64"},{"internalType":"address payable","name":"l1Recipient","type":"address"},{"internalType":"address","name":"l2Sender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint64","name":"slowRelayFeePct","type":"uint64"},{"internalType":"uint64","name":"instantRelayFeePct","type":"uint64"},{"internalType":"uint32","name":"quoteTimestamp","type":"uint32"}],"internalType":"struct BridgePool.DepositData","name":"depositData","type":"tuple"},{"components":[{"internalType":"enum BridgePool.RelayState","name":"relayState","type":"uint8"},{"internalType":"address","name":"slowRelayer","type":"address"},{"internalType":"uint32","name":"relayId","type":"uint32"},{"internalType":"uint64","name":"realizedLpFeePct","type":"uint64"},{"internalType":"uint32","name":"priceRequestTime","type":"uint32"},{"internalType":"uint256","name":"proposerBond","type":"uint256"},{"internalType":"uint256","name":"finalFee","type":"uint256"}],"internalType":"struct BridgePool.RelayData","name":"relayData","type":"tuple"}],"name":"speedUpRelay","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"store","outputs":[{"internalType":"contract StoreInterface","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"sync","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"syncUmaEcosystemParams","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"syncWithBridgeAdminParams","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"timerAddress","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"undistributedLpFees","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"utilizedReserves","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"},{"stateMutability":"payable","type":"receive"}]
*/
