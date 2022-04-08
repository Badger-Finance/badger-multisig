// contracts/RemBadgerDripper.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/finance/VestingWallet.sol";

contract RemBadgerDripper is VestingWallet {
    mapping(address => uint256) private _erc20Released;
    address private immutable _controller;
    address private immutable _governance;
    address private _keeper;

    constructor(
        address beneficiaryAddress,
        uint64 startTimestamp,
        uint64 durationSeconds,
        address keeperAddress
    ) VestingWallet(
        beneficiaryAddress,
        startTimestamp,
        durationSeconds
    ) {
        _controller = 0x86cbD0ce0c087b482782c181dA8d191De18C8275; //techops
        _governance = 0xB65cef03b9B89f99517643226d76e286ee999e77; //dev
        require(keeperAddress != address(0), "RemBadgerDripper: keeper is zero address");
        _keeper = keeperAddress;
    }

    /**
     * @dev Getter for the controller address.
     */
    function controller() public view virtual returns (address) {
        return _controller;
    }

    /**
     * @dev Getter for the governance address.
     */
    function governance() public view virtual returns (address) {
        return _governance;
    }

    /**
     * @dev Getter for the keeper address.
     */
    function keeper() public view virtual returns (address) {
        return _keeper;
    }

    /**
     * @dev Setter for the keeper address.
     */
    function setKeeper(address _newKeeper) public {
        require(
            _msgSender() == controller() || _msgSender() == governance(),
            "RemBadgerDripper: onlyAuthorized"
        );
        _keeper = _newKeeper;
    }

    function released(address token) override public view virtual returns (uint256) {
        return _erc20Released[token];
    }

    function release(address token) override public virtual {
        require(
            _msgSender() == keeper() || _msgSender() == controller() || _msgSender() == governance(),
            "RemBadgerDripper: onlyAuthorized"
        );
        uint256 releasable = vestedAmount(token, uint64(block.timestamp)) - released(token);
        _erc20Released[token] += releasable;
        emit ERC20Released(token, releasable);
        SafeERC20.safeTransfer(IERC20(token), beneficiary(), releasable);
    }
}
