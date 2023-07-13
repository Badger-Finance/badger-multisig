// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

interface IBribeMarket {
    error AlreadyInitialized();
    error DeadlinePassed();
    error InvalidAddress();
    error InvalidAmount();
    error InvalidChoiceCount();
    error InvalidDeadline();
    error InvalidIdentifier();
    error InvalidMaxPeriod();
    error InvalidPeriod();
    error InvalidPeriodDuration();
    error InvalidProtocol();
    error NoWhitelistBribeVault();
    error NotAuthorized();
    error NotTeamMember();
    error TokenNotWhitelisted();
    error TokenWhitelisted();
    error VoterBlacklisted();
    error VoterNotBlacklisted();
    event AddBlacklistedVoters(address[] voters);
    event AddWhitelistedTokens(address[] tokens);
    event GrantTeamRole(address teamMember);
    event Initialize(
        address bribeVault,
        address admin,
        string protocol,
        uint256 maxPeriods,
        uint256 periodDuration
    );
    event RemoveBlacklistedVoters(address[] voters);
    event RemoveWhitelistedTokens(address[] tokens);
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
    event SetMaxPeriods(uint256 maxPeriods);
    event SetPeriodDuration(uint256 periodDuration);
    event SetProposals(bytes32[] proposals, uint256 indexed deadline);
    event SetProposalsByAddress(bytes32[] proposals, uint256 indexed deadline);
    event SetProposalsById(
        uint256 indexed proposalIndex,
        bytes32[] proposals,
        uint256 indexed deadline
    );

    function BRIBE_VAULT() external view returns (address);

    function DEFAULT_ADMIN_ROLE() external view returns (bytes32);

    function MAX_PERIODS() external view returns (uint256);

    function MAX_PERIOD_DURATION() external view returns (uint256);

    function PROTOCOL() external view returns (string memory);

    function TEAM_ROLE() external view returns (bytes32);

    function addBlacklistedVoters(address[] memory _voters) external;

    function addWhitelistedTokens(address[] memory _tokens) external;

    function depositBribe(
        bytes32 _proposal,
        address _token,
        uint256 _amount,
        uint256 _maxTokensPerVote,
        uint256 _periods
    ) external;

    function depositBribeWithPermit(
        bytes32 _proposal,
        address _token,
        uint256 _amount,
        uint256 _maxTokensPerVote,
        uint256 _periods,
        uint256 _permitDeadline,
        bytes memory _signature
    ) external;

    function getBlacklistedVoters() external view returns (address[] memory);

    function getBribe(
        bytes32 _proposal,
        uint256 _proposalDeadline,
        address _token
    ) external view returns (address bribeToken, uint256 bribeAmount);

    function getRoleAdmin(bytes32 role) external view returns (bytes32);

    function getWhitelistedTokens() external view returns (address[] memory);

    function grantRole(bytes32 role, address account) external;

    function grantTeamRole(address _teamMember) external;

    function hasRole(bytes32 role, address account)
        external
        view
        returns (bool);

    function indexOfBlacklistedVoter(address) external view returns (uint256);

    function indexOfWhitelistedToken(address) external view returns (uint256);

    function initialize(
        address _bribeVault,
        address _admin,
        string memory _protocol,
        uint256 _maxPeriods,
        uint256 _periodDuration
    ) external;

    function isBlacklistedVoter(address _voter) external view returns (bool);

    function isWhitelistedToken(address _token) external view returns (bool);

    function maxPeriods() external view returns (uint256);

    function periodDuration() external view returns (uint256);

    function proposalDeadlines(bytes32) external view returns (uint256);

    function removeBlacklistedVoters(address[] memory _voters) external;

    function removeWhitelistedTokens(address[] memory _tokens) external;

    function renounceRole(bytes32 role, address account) external;

    function revokeRole(bytes32 role, address account) external;

    function revokeTeamRole(address _teamMember) external;

    function setMaxPeriods(uint256 _periods) external;

    function setPeriodDuration(uint256 _periodDuration) external;

    function setProposals(bytes[] memory _identifiers, uint256 _deadline)
        external;

    function setProposalsByAddress(
        address[] memory _addresses,
        uint256 _deadline
    ) external;

    function setProposalsById(
        uint256 _proposalIndex,
        uint256 _choiceCount,
        uint256 _deadline
    ) external;

    function supportsInterface(bytes4 interfaceId) external view returns (bool);
}

// THIS FILE WAS AUTOGENERATED FROM THE FOLLOWING ABI JSON:
/*
[{"inputs":[],"name":"AlreadyInitialized","type":"error"},{"inputs":[],"name":"DeadlinePassed","type":"error"},{"inputs":[],"name":"InvalidAddress","type":"error"},{"inputs":[],"name":"InvalidAmount","type":"error"},{"inputs":[],"name":"InvalidChoiceCount","type":"error"},{"inputs":[],"name":"InvalidDeadline","type":"error"},{"inputs":[],"name":"InvalidIdentifier","type":"error"},{"inputs":[],"name":"InvalidMaxPeriod","type":"error"},{"inputs":[],"name":"InvalidPeriod","type":"error"},{"inputs":[],"name":"InvalidPeriodDuration","type":"error"},{"inputs":[],"name":"InvalidProtocol","type":"error"},{"inputs":[],"name":"NoWhitelistBribeVault","type":"error"},{"inputs":[],"name":"NotAuthorized","type":"error"},{"inputs":[],"name":"NotTeamMember","type":"error"},{"inputs":[],"name":"TokenNotWhitelisted","type":"error"},{"inputs":[],"name":"TokenWhitelisted","type":"error"},{"inputs":[],"name":"VoterBlacklisted","type":"error"},{"inputs":[],"name":"VoterNotBlacklisted","type":"error"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address[]","name":"voters","type":"address[]"}],"name":"AddBlacklistedVoters","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address[]","name":"tokens","type":"address[]"}],"name":"AddWhitelistedTokens","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"teamMember","type":"address"}],"name":"GrantTeamRole","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"bribeVault","type":"address"},{"indexed":false,"internalType":"address","name":"admin","type":"address"},{"indexed":false,"internalType":"string","name":"protocol","type":"string"},{"indexed":false,"internalType":"uint256","name":"maxPeriods","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"periodDuration","type":"uint256"}],"name":"Initialize","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address[]","name":"voters","type":"address[]"}],"name":"RemoveBlacklistedVoters","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address[]","name":"tokens","type":"address[]"}],"name":"RemoveWhitelistedTokens","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"teamMember","type":"address"}],"name":"RevokeTeamRole","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"previousAdminRole","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"newAdminRole","type":"bytes32"}],"name":"RoleAdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleGranted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleRevoked","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"maxPeriods","type":"uint256"}],"name":"SetMaxPeriods","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"periodDuration","type":"uint256"}],"name":"SetPeriodDuration","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bytes32[]","name":"proposals","type":"bytes32[]"},{"indexed":true,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"SetProposals","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bytes32[]","name":"proposals","type":"bytes32[]"},{"indexed":true,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"SetProposalsByAddress","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"proposalIndex","type":"uint256"},{"indexed":false,"internalType":"bytes32[]","name":"proposals","type":"bytes32[]"},{"indexed":true,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"SetProposalsById","type":"event"},{"inputs":[],"name":"BRIBE_VAULT","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DEFAULT_ADMIN_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MAX_PERIODS","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MAX_PERIOD_DURATION","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PROTOCOL","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"TEAM_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"_voters","type":"address[]"}],"name":"addBlacklistedVoters","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"_tokens","type":"address[]"}],"name":"addWhitelistedTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_proposal","type":"bytes32"},{"internalType":"address","name":"_token","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"uint256","name":"_maxTokensPerVote","type":"uint256"},{"internalType":"uint256","name":"_periods","type":"uint256"}],"name":"depositBribe","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_proposal","type":"bytes32"},{"internalType":"address","name":"_token","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"uint256","name":"_maxTokensPerVote","type":"uint256"},{"internalType":"uint256","name":"_periods","type":"uint256"},{"internalType":"uint256","name":"_permitDeadline","type":"uint256"},{"internalType":"bytes","name":"_signature","type":"bytes"}],"name":"depositBribeWithPermit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getBlacklistedVoters","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_proposal","type":"bytes32"},{"internalType":"uint256","name":"_proposalDeadline","type":"uint256"},{"internalType":"address","name":"_token","type":"address"}],"name":"getBribe","outputs":[{"internalType":"address","name":"bribeToken","type":"address"},{"internalType":"uint256","name":"bribeAmount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleAdmin","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getWhitelistedTokens","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"grantRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_teamMember","type":"address"}],"name":"grantTeamRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"hasRole","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"indexOfBlacklistedVoter","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"indexOfWhitelistedToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_bribeVault","type":"address"},{"internalType":"address","name":"_admin","type":"address"},{"internalType":"string","name":"_protocol","type":"string"},{"internalType":"uint256","name":"_maxPeriods","type":"uint256"},{"internalType":"uint256","name":"_periodDuration","type":"uint256"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_voter","type":"address"}],"name":"isBlacklistedVoter","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_token","type":"address"}],"name":"isWhitelistedToken","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxPeriods","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"periodDuration","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"proposalDeadlines","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"_voters","type":"address[]"}],"name":"removeBlacklistedVoters","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"_tokens","type":"address[]"}],"name":"removeWhitelistedTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"renounceRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"revokeRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_teamMember","type":"address"}],"name":"revokeTeamRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_periods","type":"uint256"}],"name":"setMaxPeriods","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_periodDuration","type":"uint256"}],"name":"setPeriodDuration","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes[]","name":"_identifiers","type":"bytes[]"},{"internalType":"uint256","name":"_deadline","type":"uint256"}],"name":"setProposals","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"_addresses","type":"address[]"},{"internalType":"uint256","name":"_deadline","type":"uint256"}],"name":"setProposalsByAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_proposalIndex","type":"uint256"},{"internalType":"uint256","name":"_choiceCount","type":"uint256"},{"internalType":"uint256","name":"_deadline","type":"uint256"}],"name":"setProposalsById","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"}]
*/