// contracts/EmissionsDripper.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/finance/VestingWallet.sol";

contract EmissionsDripper is VestingWallet {
    event EtherSwept(uint256 amount);
    event ERC20Swept(address indexed token, uint256 amount);

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
            "EmissionsDripper: onlyAuthorized"
        );
        _keeper = _newKeeper;
    }

    /**
     * @dev Call VestingWallet's release method, but only on the condition
     * that the caller is authorised.
     */
    function release(address token) public override {
        require(
            _msgSender() == keeper() || _msgSender() == controller || _msgSender() == governance,
            "EmissionsDripper: onlyAuthorized"
        );
        VestingWallet.release(token);
    }

    /**
     * @dev Sweep the full contract's ether balance to governance. Can only be
     * called by governance.
     */
    function sweep() public virtual {
        require(_msgSender() == governance, "EmissionsDripper: onlyAuthorized");
        uint256 balance = address(this).balance;
        emit EtherSwept(balance);
        Address.sendValue(payable(governance), balance);
    }

    /**
     * @dev Sweep the full contract's balance for an ERC20 token to
     * governance. Can only be called by governance.
     */
    function sweep(address token) public virtual {
        require(_msgSender() == governance, "EmissionsDripper: onlyAuthorized");
        uint256 balance = IERC20(token).balanceOf(address(this));
        emit ERC20Swept(token, balance);
        SafeERC20.safeTransfer(IERC20(token), governance, balance);
    }
}
