// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.0;

interface IEToken {
    event Approval(
        address indexed owner,
        address indexed spender,
        uint256 value
    );
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
        IStorageToken.AssetConfig newConfig
    );
    event GovSetChainlinkPriceFeed(
        address indexed underlying,
        address chainlinkAggregator
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
    event RequestDonate(address indexed account, uint256 amount);
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
    event Transfer(address indexed from, address indexed to, uint256 value);
    event UnTrackAverageLiquidity(address indexed account);
    event Withdraw(
        address indexed underlying,
        address indexed account,
        uint256 amount
    );

    function allowance(address holder, address spender)
        external
        view
        returns (uint256);

    function approve(address spender, uint256 amount) external returns (bool);

    function approveSubAccount(
        uint256 subAccountId,
        address spender,
        uint256 amount
    ) external returns (bool);

    function balanceOf(address account) external view returns (uint256);

    function balanceOfUnderlying(address account)
        external
        view
        returns (uint256);

    function burn(uint256 subAccountId, uint256 amount) external;

    function convertBalanceToUnderlying(uint256 balance)
        external
        view
        returns (uint256);

    function convertUnderlyingToBalance(uint256 underlyingAmount)
        external
        view
        returns (uint256);

    function decimals() external pure returns (uint8);

    function deposit(uint256 subAccountId, uint256 amount) external;

    function donateToReserves(uint256 subAccountId, uint256 amount) external;

    function mint(uint256 subAccountId, uint256 amount) external;

    function moduleGitCommit() external view returns (bytes32);

    function moduleId() external view returns (uint256);

    function name() external view returns (string memory);

    function reserveBalance() external view returns (uint256);

    function reserveBalanceUnderlying() external view returns (uint256);

    function symbol() external view returns (string memory);

    function totalSupply() external view returns (uint256);

    function totalSupplyUnderlying() external view returns (uint256);

    function touch() external;

    function transfer(address to, uint256 amount) external returns (bool);

    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) external returns (bool);

    function transferFromMax(address from, address to) external returns (bool);

    function underlyingAsset() external view returns (address);

    function withdraw(uint256 subAccountId, uint256 amount) external;
}

interface IStorageToken {
    struct AssetConfig {
        address eTokenAddress;
        bool borrowIsolated;
        uint32 collateralFactor;
        uint32 borrowFactor;
        uint24 twapWindow;
    }
}

