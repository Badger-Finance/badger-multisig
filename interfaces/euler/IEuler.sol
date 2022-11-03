// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.0;
pragma experimental ABIEncoderV2;

interface IEuler {
    event AssetStatus(
        address indexed underlying,
        uint256 totalBalances,
        uint256 totalBorrows,
        uint96 reserveBalance,
        uint256 poolSize,
        uint256 interestAccumulator,
        int96 interestRate,
        uint256 timestamp
    );
    event Borrow(
        address indexed underlying,
        address indexed account,
        uint256 amount
    );
    event DelegateAverageLiquidity(
        address indexed account,
        address indexed delegate
    );
    event Deposit(
        address indexed underlying,
        address indexed account,
        uint256 amount
    );
    event EnterMarket(address indexed underlying, address indexed account);
    event ExitMarket(address indexed underlying, address indexed account);
    event Genesis();
    event GovConvertReserves(
        address indexed underlying,
        address indexed recipient,
        uint256 amount
    );
    event GovSetAssetConfig(
        address indexed underlying,
        IStorage.AssetConfig newConfig
    );
    event GovSetIRM(
        address indexed underlying,
        uint256 interestRateModel,
        bytes resetParams
    );
    event GovSetPricingConfig(
        address indexed underlying,
        uint16 newPricingType,
        uint32 newPricingParameter
    );
    event GovSetReserveFee(address indexed underlying, uint32 newReserveFee);
    event InstallerInstallModule(
        uint256 indexed moduleId,
        address indexed moduleImpl,
        bytes32 moduleGitCommit
    );
    event InstallerSetGovernorAdmin(address indexed newGovernorAdmin);
    event InstallerSetUpgradeAdmin(address indexed newUpgradeAdmin);
    event Liquidation(
        address indexed liquidator,
        address indexed violator,
        address indexed underlying,
        address collateral,
        uint256 repay,
        uint256 yield,
        uint256 healthScore,
        uint256 baseDiscount,
        uint256 discount
    );
    event MarketActivated(
        address indexed underlying,
        address indexed eToken,
        address indexed dToken
    );
    event PTokenActivated(address indexed underlying, address indexed pToken);
    event PTokenUnWrap(
        address indexed underlying,
        address indexed account,
        uint256 amount
    );
    event PTokenWrap(
        address indexed underlying,
        address indexed account,
        uint256 amount
    );
    event ProxyCreated(address indexed proxy, uint256 moduleId);
    event Repay(
        address indexed underlying,
        address indexed account,
        uint256 amount
    );
    event RequestBorrow(address indexed account, uint256 amount);
    event RequestBurn(address indexed account, uint256 amount);
    event RequestDeposit(address indexed account, uint256 amount);
    event RequestLiquidate(
        address indexed liquidator,
        address indexed violator,
        address indexed underlying,
        address collateral,
        uint256 repay,
        uint256 minYield
    );
    event RequestMint(address indexed account, uint256 amount);
    event RequestRepay(address indexed account, uint256 amount);
    event RequestSwap(
        address indexed accountIn,
        address indexed accountOut,
        address indexed underlyingIn,
        address underlyingOut,
        uint256 amount,
        uint256 swapType
    );
    event RequestTransferDToken(
        address indexed from,
        address indexed to,
        uint256 amount
    );
    event RequestTransferEToken(
        address indexed from,
        address indexed to,
        uint256 amount
    );
    event RequestWithdraw(address indexed account, uint256 amount);
    event TrackAverageLiquidity(address indexed account);
    event UnTrackAverageLiquidity(address indexed account);
    event Withdraw(
        address indexed underlying,
        address indexed account,
        uint256 amount
    );

    function activateMarket(address underlying) external returns (address);

    function activatePToken(address underlying) external returns (address);

    function eTokenToDToken(address eToken)
        external
        view
        returns (address dTokenAddr);

    function eTokenToUnderlying(address eToken)
        external
        view
        returns (address underlying);

    function enterMarket(uint256 subAccountId, address newMarket) external;

    function exitMarket(uint256 subAccountId, address oldMarket) external;

    function getEnteredMarkets(address account)
        external
        view
        returns (address[] memory);

    function getPricingConfig(address underlying)
        external
        view
        returns (
            uint16 pricingType,
            uint32 pricingParameters,
            address pricingForwarded
        );

    function interestAccumulator(address underlying)
        external
        view
        returns (uint256);

    function interestRate(address underlying) external view returns (int96);

    function interestRateModel(address underlying)
        external
        view
        returns (uint256);

    function moduleGitCommit() external view returns (bytes32);

    function moduleId() external view returns (uint256);

    function reserveFee(address underlying) external view returns (uint32);

    function underlyingToAssetConfig(address underlying)
        external
        view
        returns (IStorage.AssetConfig memory);

    function underlyingToAssetConfigUnresolved(address underlying)
        external
        view
        returns (IStorage.AssetConfig memory config);

    function underlyingToDToken(address underlying)
        external
        view
        returns (address);

    function underlyingToEToken(address underlying)
        external
        view
        returns (address);

    function underlyingToPToken(address underlying)
        external
        view
        returns (address);
}

interface IStorage {
    struct AssetConfig {
        address eTokenAddress;
        bool borrowIsolated;
        uint32 collateralFactor;
        uint32 borrowFactor;
        uint24 twapWindow;
    }
}