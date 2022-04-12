// contracts/RemBadgerDripper.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/finance/VestingWallet.sol";

contract RemBadgerDripper is VestingWallet {
    address public immutable controller;
    address public immutable governance;
    address private _keeper;

    constructor(
        address beneficiaryAddress,
        uint64 startTimestamp,
        uint64 durationSeconds,
        address controllerAddress,
        address governanceAddress,
        address keeperAddress
    ) VestingWallet(
        beneficiaryAddress,
        startTimestamp,
        durationSeconds
    ) {
        controller = controllerAddress;
        governance = governanceAddress;
        _keeper = keeperAddress;
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
            _msgSender() == controller || _msgSender() == governance,
            "RemBadgerDripper: onlyAuthorized"
        );
        _keeper = _newKeeper;
    }

    function release(address token) public virtual override {
        require(
            _msgSender() == keeper() || _msgSender() == controller || _msgSender() == governance,
            "RemBadgerDripper: onlyAuthorized"
        );
        VestingWallet.release(token);
    }
}
