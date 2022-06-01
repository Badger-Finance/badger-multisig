// SPDX-License-Identifier: MIT
pragma solidity >=0.5.0 <0.8.0;

interface ICrvStrategy {
    function want() external view returns (address);

    function SWAPR_ROUTER() external view returns (address);

    function gauge() external view returns (address);

    function strategist() external view returns (address);

    function controller() external view returns (address);

    function guardian() external view returns (address);

    function keeper() external view returns (address);

    function reward() external view returns (address);

    function uniswap() external view returns (address);

    function gaugeFactory() external view returns (address);

    function balanceOfPool() external view returns (uint256);

    function setGauge(address newGauge) external;

    function setGaugeFactory(address newGaugeFactory) external;

    function deposit() external;

    // NOTE: must exclude any tokens used in the yield
    // Controller role - withdraw should return to Controller
    function withdrawOther(address) external returns (uint256 balance);

    // Controller | Vault role - withdraw should always return to Vault
    function withdraw(uint256) external;

    // Controller | Vault role - withdraw should always return to Vault
    function withdrawAll() external returns (uint256);

    function balanceOf() external view returns (uint256);

    function performanceFeeStrategist() external view returns (uint256);

    function performanceFeeGovernance() external view returns (uint256);

    function getName() external pure returns (string memory);

    function setStrategist(address _strategist) external;

    function setWithdrawalFee(uint256 _withdrawalFee) external;

    function setPerformanceFeeStrategist(uint256 _performanceFeeStrategist)
        external;

    function setPerformanceFeeGovernance(uint256 _performanceFeeGovernance)
        external;

    function setGovernance(address _governance) external;

    function setController(address _controller) external;

    function tend() external;

    function harvest() external;

    function governance() external view returns (address);
}
