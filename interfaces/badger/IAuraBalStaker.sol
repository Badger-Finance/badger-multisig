// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;
pragma experimental ABIEncoderV2;

import {BaseStrategy} from "./IVestedAura.sol";

interface IAuraBalStaker {
    event Paused(address account);
    event SetWithdrawalMaxDeviationThreshold(uint256 newMaxDeviationThreshold);
    event Unpaused(address account);

    function AURA() external view returns (address);

    function AURABAL() external view returns (address);

    function AURABAL_BALETH_BPT_POOL_ID() external view returns (bytes32);

    function AURABAL_REWARDS() external view returns (address);

    function BAL() external view returns (address);

    function BALANCER_VAULT() external view returns (address);

    function BALETH_BPT() external view returns (address);

    function BAL_ETH_POOL_ID() external view returns (bytes32);

    function BB_A_USD() external view returns (address);

    function GRAVIAURA() external view returns (address);

    function MAX_BPS() external view returns (uint256);

    function WETH() external view returns (address);

    function __BaseStrategy_init(address _vault) external;

    function autoCompoundRatio() external view returns (uint256);

    function balEthBptToAuraBalMinOutBps() external view returns (uint256);

    function minBbaUsdHarvest() external view returns (uint256);

    function balanceOf() external view returns (uint256);

    function balanceOfPool() external view returns (uint256);

    function balanceOfRewards()
        external
        view
        returns (BaseStrategy.TokenAmount[] memory rewards);

    function balanceOfWant() external view returns (uint256);

    function baseStrategyVersion() external pure returns (string memory);

    function claimRewardsOnWithdrawAll() external view returns (bool);

    function deposit() external;

    function earn() external;

    function emitNonProtectedToken(address _token) external;

    function getMintableAuraRewards(uint256 _balAmount)
        external
        view
        returns (uint256 amount);

    function getName() external pure returns (string memory);

    function getProtectedTokens() external view returns (address[] memory);

    function governance() external view returns (address);

    function guardian() external view returns (address);

    function harvest()
        external
        returns (BaseStrategy.TokenAmount[] memory harvested);

    function initialize(address _vault) external;

    function isProtectedToken(address token) external view returns (bool);

    function isTendable() external pure returns (bool);

    function keeper() external view returns (address);

    function pause() external;

    function paused() external view returns (bool);

    function setBalEthBptToAuraBalMinOutBps(uint256 _minOutBps) external;

    function setClaimRewardsOnWithdrawAll(bool _claimRewardsOnWithdrawAll)
        external;

    function setWithdrawalMaxDeviationThreshold(uint256 _threshold) external;

    function setMinBbaUsdHarvest(uint256 _minBbaUsd) external;

    function strategist() external view returns (address);

    function tend() external returns (BaseStrategy.TokenAmount[] memory tended);

    function unpause() external;

    function vault() external view returns (address);

    function want() external view returns (address);

    function withdraw(uint256 _amount) external;

    function withdrawOther(address _asset) external;

    function withdrawToVault() external;

    function withdrawalMaxDeviationThreshold() external view returns (uint256);
}