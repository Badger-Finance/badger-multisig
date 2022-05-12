// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/ConfirmedOwner.sol";
import "@chainlink/contracts/src/v0.8/KeeperCompatible.sol";
import "@openzeppelin/contracts/finance/VestingWallet.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title The AutonomousDripper Contract
 * @author gosuto.eth
 * @notice A Chainlink Keeper-compatible version of OpenZeppelin's
 * VestingWallet; removing the need to monitor the interval and/or call release
 * manually. Also adds a (transferable) owner that can sweep all ether and
 * ERC-20 tokens.
 */
contract AutonomousDripper is VestingWallet, KeeperCompatibleInterface, ConfirmedOwner, Pausable {
    event EtherSwept(uint256 amount);
    event ERC20Swept(address indexed token, uint256 amount);
    event KeeperRegistryAddressUpdated(address oldAddress, address newAddress);

    error OnlyKeeperRegistry();

    uint public lastTimestamp;
    uint public immutable interval;
    address[] public assetsWatchlist;
    address private _keeperRegistryAddress;

    constructor(
        address beneficiaryAddress,
        uint64 startTimestamp,
        uint64 durationSeconds,
        uint intervalSeconds,
        address[] memory watchlistAddresses,
        address keeperRegistryAddress
    ) VestingWallet(
        beneficiaryAddress,
        startTimestamp,
        durationSeconds
    ) ConfirmedOwner(
        msg.sender
    ) {
        lastTimestamp = startTimestamp;
        interval = intervalSeconds;
        setAssetsWatchlist(watchlistAddresses);
        setKeeperRegistryAddress(keeperRegistryAddress);
    }

    /**
     * @dev Setter for the list of ERC-20 token addresses to consider for
     * releasing. Can only be called by the current owner.
     */
    function setAssetsWatchlist(address[] calldata newAssetsWatchlist) public virtual onlyOwner {
        assetsWatchlist = newAssetsWatchlist;
    }

    /**
     * @dev Loop over the assetsWatchlist and check their local balance.
     * Returns a filtered version of the assetsWatchlist for which the local
     * balance is greater than zero.
     * Strongly inspired by https://github.com/smartcontractkit/chainlink/blob/0adf6c0fb256d09e4fed2f2f86a2c027ae82535d/contracts/src/v0.8/upkeeps/EthBalanceMonitor.sol#L87-L116
     */
    function _getAssetsHeld() internal view returns (address[] memory) {
        address[] memory _assetsHeld = new address[](assetsWatchlist.length);
        uint256 count = 0;
        for (uint idx = 0; idx < assetsWatchlist.length; idx++) {
            uint256 balance = IERC20(assetsWatchlist[idx]).balanceOf(address(this));
            if (balance > 0) {
                _assetsHeld[count] = assetsWatchlist[idx];
                count++;
            }
        }
        if (count != assetsWatchlist.length) {
            assembly {
                mstore(_assetsHeld, count)
            }
        }
        return _assetsHeld;
    }

    /**
     * @dev Runs off-chain at every block to determine if the `performUpkeep`
     * function should be called on-chain.
     */
    function checkUpkeep(bytes calldata) external view override whenNotPaused returns (
        bool upkeepNeeded, bytes memory
    ) {
        if ((block.timestamp - lastTimestamp) > interval) {
            address[] memory assetsHeld = _getAssetsHeld();
            if (assetsHeld.length > 0) {
                return (true, abi.encode(assetsHeld));
            }
        }
    }

    /**
     * @dev Contains the logic that should be executed on-chain when
     * `checkUpkeep` returns true.
     */
    function performUpkeep(bytes calldata performData) external override onlyKeeperRegistry whenNotPaused {
        if ((block.timestamp - lastTimestamp) > interval) {
            address[] memory assetsHeld = abi.decode(performData, (address[]));
            for (uint idx = 0; idx < assetsHeld.length; idx++) {
                if (IERC20(assetsHeld[idx]).balanceOf(address(this)) > 0) {
                    VestingWallet.release(assetsHeld[idx]);
                    lastTimestamp = block.timestamp;
                }
            }
        }
    }

    /**
     * @dev Sweep the full contract's ether balance to the current owner. Can
     * only be called by the current owner.
     */
    function sweep() public virtual onlyOwner {
        uint256 balance = address(this).balance;
        emit EtherSwept(balance);
        Address.sendValue(payable(super.owner()), balance);
    }

    /**
     * @dev Sweep the full contract's balance for an ERC-20 token to the
     * current owner. Can only be called by the current owner.
     */
    function sweep(address token) public virtual onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        emit ERC20Swept(token, balance);
        SafeERC20.safeTransfer(IERC20(token), super.owner(), balance);
    }

    /**
    * @dev Getter for the keeper registry address.
    */
    function getKeeperRegistryAddress() external view returns (address keeperRegistryAddress) {
        return _keeperRegistryAddress;
    }

    /**
    * @dev Setter for the keeper registry address.
    */
    function setKeeperRegistryAddress(address keeperRegistryAddress) public onlyOwner {
        require(keeperRegistryAddress != address(0));
        emit KeeperRegistryAddressUpdated(_keeperRegistryAddress, keeperRegistryAddress);
        _keeperRegistryAddress = keeperRegistryAddress;
    }

    /**
    * @dev Pauses the contract, which prevents executing performUpkeep.
    */
    function pause() external onlyOwner {
        _pause();
    }

    /**
    * @dev Unpauses the contract.
    */
    function unpause() external onlyOwner {
        _unpause();
    }

    modifier onlyKeeperRegistry() {
        if (msg.sender != _keeperRegistryAddress) {
            revert OnlyKeeperRegistry();
        }
        _;
    }
}