// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.4.24;

interface IWBTC {
    function mintingFinished() external view returns (bool);

    function name() external view returns (string memory);

    function approve(address _spender, uint256 _value) external returns (bool);

    function reclaimToken(address _token) external;

    function totalSupply() external view returns (uint256);

    function transferFrom(
        address _from,
        address _to,
        uint256 _value
    ) external returns (bool);

    function decimals() external view returns (uint8);

    function unpause() external;

    function mint(address _to, uint256 _amount) external returns (bool);

    function burn(uint256 value) external;

    function claimOwnership() external;

    function paused() external view returns (bool);

    function decreaseApproval(address _spender, uint256 _subtractedValue)
        external
        returns (bool success);

    function balanceOf(address _owner) external view returns (uint256);

    function renounceOwnership() external;

    function finishMinting() external returns (bool);

    function pause() external;

    function owner() external view returns (address);

    function symbol() external view returns (string memory);

    function transfer(address _to, uint256 _value) external returns (bool);

    function increaseApproval(address _spender, uint256 _addedValue)
        external
        returns (bool success);

    function allowance(address _owner, address _spender)
        external
        view
        returns (uint256);

    function pendingOwner() external view returns (address);

    function transferOwnership(address newOwner) external;

    event Pause();
    event Unpause();
    event Burn(address indexed burner, uint256 value);
    event Mint(address indexed to, uint256 amount);
    event MintFinished();
    event OwnershipRenounced(address indexed previousOwner);
    event OwnershipTransferred(
        address indexed previousOwner,
        address indexed newOwner
    );
    event Approval(
        address indexed owner,
        address indexed spender,
        uint256 value
    );
    event Transfer(address indexed from, address indexed to, uint256 value);
}
