// SPDX-License-Identifier: MIT
pragma solidity >=0.5.0 <0.8.0;

interface ISimpleWrapperGatedUpgradeable {
    event SetTreasury(address treasury);

    function affiliate() external view returns (address);

    function approve(address spender, uint256 amount) external returns (bool);

    function deposit(uint256 amount, bytes32[] calldata merkleProof) external;
    
    function guardian() external view returns (address);

    function manager() external view returns (address);
    
    function withdrawalFee() external view returns (address);
    
    function withdrawalMaxDeviationThreshold() external view returns (address);
    
    function experimentalVault() external view returns (address);

    function experimentalMode() external view returns (address);
    
    function treasury() external view returns (address);

    function token() external view returns (address);
    
    function GAC() external view returns (address);

    function setTreasury(address _treasury) external;

    function balanceOf(address account) external view returns (uint256);

    function withdraw(uint256 _shares) external;

    function withdraw() external returns (uint256);

    function transfer(address recipient, uint256 amount) external returns (bool);
}
