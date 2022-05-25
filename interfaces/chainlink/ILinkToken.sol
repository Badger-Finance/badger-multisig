// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.4.24;

interface ILinkToken {
    function name() external view returns (string memory);

    function approve(address _spender, uint256 _value) external returns (bool);

    function totalSupply() external view returns (uint256);

    function transferFrom(
        address _from,
        address _to,
        uint256 _value
    ) external returns (bool);

    function decimals() external view returns (uint8);

    function transferAndCall(
        address _to,
        uint256 _value,
        bytes _data
    ) external returns (bool success);

    function decreaseApproval(address _spender, uint256 _subtractedValue)
        external
        returns (bool success);

    function balanceOf(address _owner) external view returns (uint256 balance);

    function symbol() external view returns (string memory);

    function transfer(address _to, uint256 _value)
        external
        returns (bool success);

    function increaseApproval(address _spender, uint256 _addedValue)
        external
        returns (bool success);

    function allowance(address _owner, address _spender)
        external
        view
        returns (uint256 remaining);

    event Transfer(
        address indexed from,
        address indexed to,
        uint256 value,
        bytes data
    );
    event Approval(
        address indexed owner,
        address indexed spender,
        uint256 value
    );
    event Transfer(address indexed from, address indexed to, uint256 value);
}
