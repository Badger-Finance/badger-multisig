// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.7;

interface IVotiumBribe {
    event Bribed(
        address _token,
        uint256 _amount,
        bytes32 indexed _proposal,
        uint256 _choiceIndex
    );
    event Initiated(bytes32 _proposal);
    event ModifiedTeam(address _member, bool _approval);
    event OwnershipTransferred(
        address indexed previousOwner,
        address indexed newOwner
    );
    event UpdatedDistributor(address indexed _token, address _distributor);
    event UpdatedFee(uint256 _feeAmount);
    event WhitelistRequirement(bool _requireWhitelist);
    event Whitelisted(address _token);

    function DENOMINATOR() external view returns (uint256);

    function approveDelegationVote(bytes32 _hash) external;

    function approvedTeam(address) external view returns (bool);

    function delegationHash(bytes32) external view returns (bool);

    function depositBribe(
        address _token,
        uint256 _amount,
        bytes32 _proposal,
        uint256 _choiceIndex
    ) external;

    function feeAddress() external view returns (address);

    function initiateProposal(
        bytes32 _proposal,
        uint256 _deadline,
        uint256 _maxIndex
    ) external;

    function isWinningSignature(bytes32 _hash, bytes memory _signature)
        external
        view
        returns (bool);

    function modifyTeam(address _member, bool _approval) external;

    function owner() external view returns (address);

    function platformFee() external view returns (uint256);

    function proposalInfo(bytes32)
        external
        view
        returns (uint256 deadline, uint256 maxIndex);

    function requireWhitelist() external view returns (bool);

    function setWhitelistRequired(bool _requireWhitelist) external;

    function tokenInfo(address)
        external
        view
        returns (bool whitelist, address distributor);

    function transferOwnership(address newOwner) external;

    function transferToDistributor(address _token) external;

    function updateDistributor(address _token, address _distributor) external;

    function updateFeeAddress(address _feeAddress) external;

    function updateFeeAmount(uint256 _feeAmount) external;

    function whitelistToken(address _token) external;

    function whitelistTokens(address[] memory _tokens) external;
}
