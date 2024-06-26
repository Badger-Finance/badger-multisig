// SPDX-License-Identifier: GPL-3.0

pragma solidity 0.8.15;
pragma abicoder v2;

interface IBunniToken {
    event Approval(
        address indexed owner,
        address indexed spender,
        uint256 value
    );
    event Transfer(address indexed from, address indexed to, uint256 value);

    function DOMAIN_SEPARATOR() external view returns (bytes32);

    function allowance(address, address) external view returns (uint256);

    function approve(address spender, uint256 amount) external returns (bool);

    function balanceOf(address) external view returns (uint256);

    function burn(address from, uint256 amount) external;

    function decimals() external view returns (uint8);

    function hub() external view returns (address);

    function mint(address to, uint256 amount) external;

    function name() external view returns (string memory);

    function nonces(address) external view returns (uint256);

    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;

    function pool() external view returns (address);

    function symbol() external view returns (string memory);

    function tickLower() external view returns (int24);

    function tickUpper() external view returns (int24);

    function totalSupply() external view returns (uint256);

    function transfer(address to, uint256 amount) external returns (bool);

    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) external returns (bool);
}

struct BunniKey {
    address pool;
    int24 tickLower;
    int24 tickUpper;
}
