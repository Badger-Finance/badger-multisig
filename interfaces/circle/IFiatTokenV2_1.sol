// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

interface IFiatTokenV2_1 {
    event Approval(
        address indexed owner,
        address indexed spender,
        uint256 value
    );
    event AuthorizationCanceled(
        address indexed authorizer,
        bytes32 indexed nonce
    );
    event AuthorizationUsed(address indexed authorizer, bytes32 indexed nonce);
    event Blacklisted(address indexed _account);
    event BlacklisterChanged(address indexed newBlacklister);
    event Burn(address indexed burner, uint256 amount);
    event MasterMinterChanged(address indexed newMasterMinter);
    event Mint(address indexed minter, address indexed to, uint256 amount);
    event MinterConfigured(address indexed minter, uint256 minterAllowedAmount);
    event MinterRemoved(address indexed oldMinter);
    event OwnershipTransferred(address previousOwner, address newOwner);
    event Pause();
    event PauserChanged(address indexed newAddress);
    event RescuerChanged(address indexed newRescuer);
    event Transfer(address indexed from, address indexed to, uint256 value);
    event UnBlacklisted(address indexed _account);
    event Unpause();

    function CANCEL_AUTHORIZATION_TYPEHASH() external view returns (bytes32);

    function DOMAIN_SEPARATOR() external view returns (bytes32);

    function PERMIT_TYPEHASH() external view returns (bytes32);

    function RECEIVE_WITH_AUTHORIZATION_TYPEHASH()
        external
        view
        returns (bytes32);

    function TRANSFER_WITH_AUTHORIZATION_TYPEHASH()
        external
        view
        returns (bytes32);

    function allowance(address owner, address spender)
        external
        view
        returns (uint256);

    function approve(address spender, uint256 value) external returns (bool);

    function authorizationState(address authorizer, bytes32 nonce)
        external
        view
        returns (bool);

    function balanceOf(address account) external view returns (uint256);

    function blacklist(address _account) external;

    function blacklister() external view returns (address);

    function burn(uint256 _amount) external;

    function cancelAuthorization(
        address authorizer,
        bytes32 nonce,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;

    function configureMinter(address minter, uint256 minterAllowedAmount)
        external
        returns (bool);

    function currency() external view returns (string memory);

    function decimals() external view returns (uint8);

    function decreaseAllowance(address spender, uint256 decrement)
        external
        returns (bool);

    function increaseAllowance(address spender, uint256 increment)
        external
        returns (bool);

    function initialize(
        string calldata tokenName,
        string calldata tokenSymbol,
        string calldata tokenCurrency,
        uint8 tokenDecimals,
        address newMasterMinter,
        address newPauser,
        address newBlacklister,
        address newOwner
    ) external;

    function initializeV2(string calldata newName) external;

    function initializeV2_1(address lostAndFound) external;

    function isBlacklisted(address _account) external view returns (bool);

    function isMinter(address account) external view returns (bool);

    function masterMinter() external view returns (address);

    function mint(address _to, uint256 _amount) external returns (bool);

    function minterAllowance(address minter) external view returns (uint256);

    function name() external view returns (string memory);

    function nonces(address owner) external view returns (uint256);

    function owner() external view returns (address);

    function pause() external;

    function paused() external view returns (bool);

    function pauser() external view returns (address);

    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;

    function receiveWithAuthorization(
        address from,
        address to,
        uint256 value,
        uint256 validAfter,
        uint256 validBefore,
        bytes32 nonce,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;

    function removeMinter(address minter) external returns (bool);

    function rescueERC20(
        address tokenContract,
        address to,
        uint256 amount
    ) external;

    function rescuer() external view returns (address);

    function symbol() external view returns (string memory);

    function totalSupply() external view returns (uint256);

    function transfer(address to, uint256 value) external returns (bool);

    function transferFrom(
        address from,
        address to,
        uint256 value
    ) external returns (bool);

    function transferOwnership(address newOwner) external;

    function transferWithAuthorization(
        address from,
        address to,
        uint256 value,
        uint256 validAfter,
        uint256 validBefore,
        bytes32 nonce,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;

    function unBlacklist(address _account) external;

    function unpause() external;

    function updateBlacklister(address _newBlacklister) external;

    function updateMasterMinter(address _newMasterMinter) external;

    function updatePauser(address _newPauser) external;

    function updateRescuer(address newRescuer) external;

    function version() external view returns (string memory);
}
