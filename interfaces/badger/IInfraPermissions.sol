pragma solidity >=0.7.0 <0.9.0;

interface IInfraPermissions {
    function strategist() external view returns (address);

    function governance() external view returns (address);

    function owner() external view returns (address);

    function manager() external view returns (address);

    function admin() external view returns (address);

    function guardian() external view returns (address);
}