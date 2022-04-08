// contracts/RemBadgerDripper.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/finance/VestingWallet.sol";

contract RemBadgerDripper is VestingWallet {
    address public constant controller = 0x86cbD0ce0c087b482782c181dA8d191De18C8275;
    address public constant governance = 0xB65cef03b9B89f99517643226d76e286ee999e77;
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
        require(keeperAddress != address(0), "RemBadgerDripper: keeper is zero address");
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
