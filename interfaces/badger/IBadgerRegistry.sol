// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

interface IBadgerRegistry {
    event AddKey(string key);
    event AddVersion(string version);
    event DemoteVault(
        address author,
        string version,
        address vault,
        uint8 status
    );
    event NewVault(address author, string version, address vault);
    event PromoteVault(
        address author,
        string version,
        address vault,
        uint8 status
    );
    event RemoveVault(address author, string version, address vault);
    event Set(string key, address at);

    function add(string memory version, address vault) external;

    function addVersions(string memory version) external;

    function addresses(string memory) external view returns (address);

    function demote(
        string memory version,
        address vault,
        uint8 status
    ) external;

    function devGovernance() external view returns (address);

    function get(string memory key) external view returns (address);

    function getFilteredProductionVaults(string memory version, uint8 status)
        external
        view
        returns (address[] memory);

    function getProductionVaults()
        external
        view
        returns (BadgerRegistry.VaultData[] memory);

    function getVaults(string memory version, address author)
        external
        view
        returns (address[] memory);

    function governance() external view returns (address);

    function initialize(address newGovernance) external;

    function keys(uint256) external view returns (string memory);

    function promote(
        string memory version,
        address vault,
        uint8 status
    ) external;

    function remove(string memory version, address vault) external;

    function set(string memory key, address at) external;

    function setDev(address newDev) external;

    function setGovernance(address _newGov) external;

    function versions(uint256) external view returns (string memory);
}

interface BadgerRegistry {
    struct VaultData {
        string version;
        uint8 status;
        address[] list;
    }
}