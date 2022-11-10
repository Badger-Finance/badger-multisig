// SPDX-License-Identifier: MIT

pragma solidity ^0.6.0;

interface ICore {
    enum PeakState { Extinct, Active, RedeemOnly, MintOnly }

    function mint(
        uint256 btc,
        address account,
        bytes32[] calldata merkleProof
    ) external returns (uint256);

    function redeem(uint256 btc, address account) external returns (uint256);

    function btcToBbtc(uint256 btc) external view returns (uint256, uint256);

    function bBtcToBtc(uint256 bBtc) external view returns (uint256 btc, uint256 fee);

    function pricePerShare() external view returns (uint256);

    function setGuestList(address guestlist) external;

    function setPeakStatus(address peak, PeakState state) external;

    function collectFee() external;

    function owner() external view returns (address);

    function feeSink() external view returns (address);

    function mintFee() external view returns (uint256);

    function redeemFee() external view returns (uint256);

    function accumulatedFee() external view returns (uint256);

    function guestList() external view returns (address);

    function bBTC() external view returns (address);

    function peaks(address) external view returns (uint256);

    function guardian() external view returns (address);

    function setGuardian(address) external;

    function paused() external view returns (bool);

    function unpause() external;

    function pause() external;
}