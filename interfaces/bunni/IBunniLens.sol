// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.15;

interface IBunniLens {
    error T();

    function getReserves(BunniKey memory key)
        external
        view
        returns (uint112 reserve0, uint112 reserve1);

    function hub() external view returns (address);

    function pricePerFullShare(BunniKey memory key)
        external
        view
        returns (
            uint128 liquidity,
            uint256 amount0,
            uint256 amount1
        );
}

struct BunniKey {
    address pool;
    int24 tickLower;
    int24 tickUpper;
}
