// contracts/EmissionsDripper.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/finance/VestingWallet.sol";
import "@chainlink/contracts/src/v0.8/KeeperCompatible.sol";

/**
 * @title The AutonomousDripper Contract
 * @author gosuto.eth
 * @notice A Chainlink Keeper-compatible version of OpenZeppelin's
 * VestingWallet; removing the need to monitor the interval and/or call release
 * manually. Also adds an admin that can sweep all ether and ERC-20 tokens.
 */
contract AutonomousDripper is VestingWallet, KeeperCompatibleInterface {
    event EtherSwept(uint256 amount);
    event ERC20Swept(address indexed token, uint256 amount);

    address private _admin;
    uint public lastTimestamp;
    uint public immutable interval;
    address[] public assetsWatchlist;

    constructor(
        address beneficiaryAddress,
        uint64 startTimestamp,
        uint64 durationSeconds,
        address adminAddress,
        uint intervalSeconds,
        address[] memory watchlistAddresses
    ) VestingWallet(
        beneficiaryAddress,
        startTimestamp,
        durationSeconds
    ) {
        _admin = adminAddress;
        lastTimestamp = startTimestamp;
        interval = intervalSeconds;
        assetsWatchlist = watchlistAddresses;
    }

    /**
     * @dev Setter for the list of ERC-20 token addresses to consider for
     * releasing. Can only be called by the admin.
     */
    function setAssetsWatchlist(address[] calldata newAssetsWatchlist) public virtual {
        require(_msgSender() == _admin, "AutonomousDripper: onlyAdmin");
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
    function checkUpkeep(bytes calldata) external view override returns (
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
    function performUpkeep(bytes calldata performData) external override {
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
     * @dev Getter for the admin address.
     */
    function admin() public view virtual returns (address) {
        return _admin;
    }

    /**
     * @dev Setter for the admin address. Can only be called by the admin.
     */
    function swapAdmin(address _newAdmin) public {
        require(_msgSender() == _admin, "AutonomousDripper: onlyAdmin");
        _admin = _newAdmin;
    }

    /**
     * @dev Sweep the full contract's ether balance to the admin. Can only be
     * called by the admin.
     */
    function sweep() public virtual {
        require(_msgSender() == _admin, "AutonomousDripper: onlyAdmin");
        uint256 balance = address(this).balance;
        emit EtherSwept(balance);
        Address.sendValue(payable(_admin), balance);
    }

    /**
     * @dev Sweep the full contract's balance for an ERC-20 token to the admin.
     * Can only be called by the admin.
     */
    function sweep(address token) public virtual {
        require(_msgSender() == _admin, "AutonomousDripper: onlyAdmin");
        uint256 balance = IERC20(token).balanceOf(address(this));
        emit ERC20Swept(token, balance);
        SafeERC20.safeTransfer(IERC20(token), _admin, balance);
    }
}
