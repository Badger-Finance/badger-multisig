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
 * manually. Also adds an owner that can sweep all ether and ERC-20 tokens.
 */
contract AutonomousDripper is VestingWallet, KeeperCompatibleInterface {
    event EtherSwept(uint256 amount);
    event ERC20Swept(address indexed token, uint256 amount);

    address private _owner;
    uint public lastTimestamp;
    uint public immutable interval;
    // TODO: write setter methods that can add or remove entries from this list
    address[] public assetsWatchlist;

    constructor(
        address beneficiaryAddress,
        uint64 startTimestamp,
        uint64 durationSeconds,
        address ownerAddress,
        uint intervalSeconds,
        address[] memory watchlistAddresses
    ) VestingWallet(
        beneficiaryAddress,
        startTimestamp,
        durationSeconds
    ) {
        _owner = ownerAddress;
        lastTimestamp = startTimestamp;
        interval = intervalSeconds;
        assetsWatchlist = watchlistAddresses;
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
        address[] memory assetsHeld = new address[](assetsWatchlist.length);
        uint256 count = 0;

        if ((block.timestamp - lastTimestamp) > interval) {
            assetsHeld = _getAssetsHeld();
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
            lastTimestamp = block.timestamp;
            address[] memory assetsHeld = abi.decode(performData, (address[]));
            for (uint idx = 0; idx < assetsHeld.length; idx++) {
                if (IERC20(assetsHeld[idx]).balanceOf(address(this)) > 0) {
                    VestingWallet.release(assetsHeld[idx]);
                }
            }
        }
    }

    /**
     * @dev Getter for the owner address.
     */
    function owner() public view virtual returns (address) {
        return _owner;
    }

    /**
     * @dev Setter for the owner address.
     */
    function swapOwner(address _newOwner) public {
        require(_msgSender() == _owner, "AutonomousDripper: onlyOwner");
        _owner = _newOwner;
    }

    /**
     * @dev Sweep the full contract's ether balance to the owner. Can only be
     * called by the owner.
     */
    function sweep() public virtual {
        require(_msgSender() == _owner, "AutonomousDripper: onlyOwner");
        uint256 balance = address(this).balance;
        emit EtherSwept(balance);
        Address.sendValue(payable(_owner), balance);
    }

    /**
     * @dev Sweep the full contract's balance for an ERC20 token to the owner.
     * Can only be called by the owner.
     */
    function sweep(address token) public virtual {
        require(_msgSender() == _owner, "AutonomousDripper: onlyOwner");
        uint256 balance = IERC20(token).balanceOf(address(this));
        emit ERC20Swept(token, balance);
        SafeERC20.safeTransfer(IERC20(token), _owner, balance);
    }
}
