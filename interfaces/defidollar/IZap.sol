// SPDX-License-Identifier: MIT

pragma solidity 0.6.11;

interface IZap {
    function mint(address token, uint amount, uint poolId, uint idx, uint minOut)
        external
        returns(uint _ibbtc);

    function redeem(address token, uint amount, uint poolId, int128 idx, uint minOut)
        external
        returns(uint out);
}
