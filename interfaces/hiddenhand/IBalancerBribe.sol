// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

interface IBalancerBribe {
    event AddWhitelistTokens(address[] tokens);
    event DepositBribe(
        bytes32 indexed proposal,
        address indexed token,
        uint256 amount,
        bytes32 bribeIdentifier,
        bytes32 rewardIdentifier,
        address indexed briber
    );
    event GrantTeamRole(address teamMember);
    event RemoveWhitelistTokens(address[] tokens);
    event RevokeTeamRole(address teamMember);
    event RoleAdminChanged(
        bytes32 indexed role,
        bytes32 indexed previousAdminRole,
        bytes32 indexed newAdminRole
    );
    event RoleGranted(
        bytes32 indexed role,
        address indexed account,
        address indexed sender
    );
    event RoleRevoked(
        bytes32 indexed role,
        address indexed account,
        address indexed sender
    );
    event SetProposal(bytes32 indexed proposal, uint256 deadline);
    event SetRewardForwarding(address from, address to);

    function BRIBE_VAULT() external view returns (address);

    function DEFAULT_ADMIN_ROLE() external view returns (bytes32);

    function PROTOCOL() external view returns (bytes32);

    function TEAM_ROLE() external view returns (bytes32);

    function addWhitelistTokens(address[] memory tokens) external;

    function allWhitelistedTokens(uint256) external view returns (address);

    function depositBribe(bytes32 proposal) external payable;

    function depositBribeERC20(
        bytes32 proposal,
        address token,
        uint256 amount
    ) external;

    function gauges(uint256) external view returns (address);

    function generateBribeVaultIdentifier(
        bytes32 proposal,
        uint256 proposalDeadline,
        address token
    ) external view returns (bytes32 identifier);

    function generateRewardIdentifier(uint256 proposalDeadline, address token)
        external
        view
        returns (bytes32 identifier);

    function getBribe(
        bytes32 proposal,
        uint256 proposalDeadline,
        address token
    ) external view returns (address bribeToken, uint256 bribeAmount);

    function getGauges() external view returns (address[] memory);

    function getRoleAdmin(bytes32 role) external view returns (bytes32);

    function getWhitelistedTokens() external view returns (address[] memory);

    function grantRole(bytes32 role, address account) external;

    function grantTeamRole(address teamMember) external;

    function hasRole(bytes32 role, address account)
        external
        view
        returns (bool);

    function indexOfGauge(address) external view returns (uint256);

    function indexOfWhitelistedToken(address) external view returns (uint256);

    function isWhitelistedToken(address token) external view returns (bool);

    function proposalDeadlines(bytes32) external view returns (uint256);

    function removeWhitelistTokens(address[] memory tokens) external;

    function renounceRole(bytes32 role, address account) external;

    function revokeRole(bytes32 role, address account) external;

    function revokeTeamRole(address teamMember) external;

    function rewardForwarding(address) external view returns (address);

    function setGaugeProposal(address gauge, uint256 deadline) external;

    function setGaugeProposals(
        address[] memory gauges_,
        uint256[] memory deadlines
    ) external;

    function setRewardForwarding(address to) external;

    function supportsInterface(bytes4 interfaceId) external view returns (bool);
}
