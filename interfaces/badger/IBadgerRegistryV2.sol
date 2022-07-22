// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

interface IBadgerRegistryV2 {
  event NewVault(address author, string version, string metadata, address vault);
  event RemoveVault(address author, string version, string metadata, address vault);
  event PromoteVault(address author, string version, string metadata, address vault, VaultStatus status);
  event DemoteVault(address author, string version, string metadata, address vault, VaultStatus status);
  event PurgeVault(address author, string version, string metadata, address vault, VaultStatus status);

  event Set(string key, address at);
  event AddKey(string key);
  event DeleteKey(string key);
  event AddVersion(string version);

  enum VaultStatus {
    deprecated,
    experimental,
    guarded,
    open
  }
  
  struct VaultInfo {
    address vault;
    string version;
    VaultStatus status;
    string metadata;
  }

  struct VaultMetadata {
    address vault;
    string metadata;
  }

  struct VaultData {
    string version;
    VaultStatus status;
    VaultMetadata[] list;
  }

  function setGovernance(address _newGov) external;
  function setDeveloper(address newDev) external;
  function setStrategistGuild(address newStrategistGuild) external;
  function addVersions(string memory version) external;
  function add(
    address vault,
    string memory version,
    string memory metadata
  ) external;
  function promote(
    address vault,
    string memory version,
    string memory metadata,
    VaultStatus status
  ) external;
  function demote(address vault, VaultStatus status) external;
  function purge(address vault) external;
  function updateMetadata(address vault, string memory metadata) external;
  function set(string memory key, address at) external;
  function deleteKey(string memory key) external;
  function deleteKeys(string[] memory _keys) external;
	function governance() external view returns (address);
	function developer() external view returns (address);
	function strategistGuild() external view returns (address);
  function get(string memory key) external view returns (address);
  function keysCount() external view returns (uint256);
  function getVaults(string memory version, address author) external view returns (VaultInfo[] memory);
  function getFilteredProductionVaults(string memory version, VaultStatus status)
    external
    view
    returns (VaultInfo[] memory);
  function getProductionVaults() external view returns (VaultData[] memory);
}
