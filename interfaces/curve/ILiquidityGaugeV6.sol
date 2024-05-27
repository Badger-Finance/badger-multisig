// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0;

interface ILiquidityGaugeV6 {
    function deposit_reward_token(address _reward_token, uint256 _amount, uint256 _epoch) external;
}